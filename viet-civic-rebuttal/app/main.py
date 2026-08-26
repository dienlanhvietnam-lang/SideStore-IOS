from __future__ import annotations

from pathlib import Path

import aiofiles
from fastapi import BackgroundTasks, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.models import JobRecord, JobStatus
from app.pipeline.media import sanitize_filename
from app.pipeline.runner import load_job, new_job_id, run_pipeline, save_job

ROOT = Path(__file__).resolve().parent
settings = get_settings()

app = FastAPI(
    title="Phản biện công dân",
    description="MVP phân tích video ngắn và soạn phản biện văn xuôi tiếng Việt.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "title": "Phản biện công dân",
            "has_llm": settings.has_llm,
            "demo_mode": settings.allow_demo_mode and not settings.has_llm,
            "port": settings.port,
        },
    )


@app.get("/viec/{job_id}", response_class=HTMLResponse)
async def job_page(request: Request, job_id: str) -> HTMLResponse:
    job = load_job(job_id)
    if job is None:
        return templates.TemplateResponse(
            request,
            "not_found.html",
            {"title": "Không tìm thấy", "job_id": job_id},
            status_code=404,
        )
    return templates.TemplateResponse(
        request,
        "job.html",
        {"title": f"Việc {job_id}", "job": job},
    )


@app.get("/api/viec/{job_id}")
async def job_api(job_id: str) -> JSONResponse:
    job = load_job(job_id)
    if job is None:
        return JSONResponse({"error": "Không tìm thấy việc."}, status_code=404)
    return JSONResponse(job.model_dump(mode="json"))


@app.post("/api/phan-tich", response_model=None)
async def create_analysis(
    background_tasks: BackgroundTasks,
    video: UploadFile | None = File(default=None),
    url: str = Form(default=""),
    transcript: str = Form(default=""),
    source_label: str = Form(default=""),
):
    url = (url or "").strip()
    transcript = (transcript or "").strip()
    label = (source_label or "").strip()

    has_video = video is not None and bool(video.filename)
    if not has_video and not url and not transcript:
        return JSONResponse(
            {
                "error": "Cần tải lên video, dán liên kết, hoặc nhập bản ghi lời thoại."
            },
            status_code=400,
        )

    job_id = new_job_id()
    source_type = "transcript"
    if has_video:
        source_type = "upload"
    elif url:
        source_type = "url"

    job = JobRecord(
        id=job_id,
        status=JobStatus.queued,
        source_type=source_type,
        source_label=label or (video.filename if has_video else url) or "Bản ghi tay",
        progress_message="Đã nhận yêu cầu, bắt đầu xử lý…",
    )
    save_job(job)

    video_path: Path | None = None
    if has_video and video is not None:
        safe = sanitize_filename(video.filename or "video.mp4")
        video_path = settings.uploads_dir / f"{job_id}_{safe}"
        async with aiofiles.open(video_path, "wb") as out:
            while True:
                chunk = await video.read(1024 * 1024)
                if not chunk:
                    break
                await out.write(chunk)
        job.meta["upload_path"] = str(video_path)
        save_job(job)

    background_tasks.add_task(
        _run_job_sync,
        job_id,
        str(video_path) if video_path else None,
        url or None,
        transcript or None,
    )
    return RedirectResponse(url=f"/viec/{job_id}", status_code=303)


def _run_job_sync(
    job_id: str,
    video_path: str | None,
    source_url: str | None,
    manual_transcript: str | None,
) -> None:
    run_pipeline(
        job_id,
        video_path=Path(video_path) if video_path else None,
        source_url=source_url,
        manual_transcript=manual_transcript,
    )


@app.post("/api/viec/{job_id}/cap-nhat-van-xoi")
async def update_prose(job_id: str, request: Request) -> JSONResponse:
    job = load_job(job_id)
    if job is None or job.analysis is None:
        return JSONResponse({"error": "Không tìm thấy kết quả."}, status_code=404)
    body = await request.json()
    prose = (body.get("phan_bien_van_xoi") or "").strip()
    if len(prose) < 40:
        return JSONResponse(
            {"error": "Phản biện văn xuôi quá ngắn."}, status_code=400
        )
    job.analysis.phan_bien_van_xoi = prose
    job.touch(message="Đã lưu bản chỉnh sửa của biên tập viên.")
    save_job(job)
    return JSONResponse({"ok": True, "message": "Đã lưu."})


@app.get("/suc-khoe")
async def health() -> dict:
    return {
        "ok": True,
        "dich_vu": "phan-bien-cong-dan",
        "cong": settings.port,
        "co_llm": settings.has_llm,
        "che_do_demo": settings.allow_demo_mode and not settings.has_llm,
    }


def create_app() -> FastAPI:
    return app
