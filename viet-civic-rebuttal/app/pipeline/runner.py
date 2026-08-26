from __future__ import annotations

import shutil
import traceback
import uuid
from pathlib import Path

from app.config import Settings, get_settings
from app.models import JobRecord, JobStatus
from app.pipeline.analyze import analyze_with_llm
from app.pipeline.asr import transcribe_audio
from app.pipeline.media import (
    describe_frames_heuristic,
    download_url,
    extract_audio,
    read_json,
    sample_frames,
    write_json,
)


def job_path(job_id: str, settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    return settings.jobs_dir / f"{job_id}.json"


def save_job(job: JobRecord, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    write_json(job_path(job.id, settings), job.model_dump(mode="json"))


def load_job(job_id: str, settings: Settings | None = None) -> JobRecord | None:
    settings = settings or get_settings()
    path = job_path(job_id, settings)
    if not path.exists():
        return None
    return JobRecord.model_validate(read_json(path))


def new_job_id() -> str:
    return uuid.uuid4().hex[:12]


def run_pipeline(
    job_id: str,
    *,
    video_path: Path | None = None,
    source_url: str | None = None,
    manual_transcript: str | None = None,
) -> None:
    settings = get_settings()
    job = load_job(job_id, settings)
    if job is None:
        return

    work = settings.jobs_dir / job_id
    work.mkdir(parents=True, exist_ok=True)

    try:
        local_video: Path | None = video_path

        if source_url:
            job.touch(JobStatus.downloading, "Đang tải video từ liên kết…")
            save_job(job, settings)
            local_video = download_url(source_url, work / "download")
            job.source_label = job.source_label or source_url
            job.meta["video_path"] = str(local_video)

        transcript = (manual_transcript or "").strip()

        if local_video and local_video.exists():
            job.touch(JobStatus.extracting, "Đang tách âm thanh và khung hình…")
            save_job(job, settings)
            audio = work / "audio.wav"
            extract_audio(local_video, audio)
            frames = sample_frames(local_video, work / "frames")
            job.frame_notes = describe_frames_heuristic(frames)
            job.meta["frame_count"] = len(frames)
            job.meta["audio_path"] = str(audio)

            if not transcript:
                job.touch(JobStatus.transcribing, "Đang nhận dạng giọng nói tiếng Việt…")
                save_job(job, settings)
                transcript = transcribe_audio(audio, settings)
        elif not transcript:
            raise RuntimeError(
                "Không có video và cũng không có bản ghi lời thoại để phân tích."
            )

        job.transcript = transcript
        job.touch(JobStatus.analyzing, "Đang phân tích và soạn phản biện văn xuôi…")
        save_job(job, settings)

        analysis = analyze_with_llm(
            transcript=transcript,
            frame_notes=job.frame_notes,
            source_label=job.source_label,
            source_type=job.source_type,
            settings=settings,
        )
        job.analysis = analysis
        job.touch(JobStatus.done, "Hoàn tất. Có thể đọc và chỉnh phản biện.")
        save_job(job, settings)
    except Exception as exc:  # noqa: BLE001 — ghi lỗi đầy đủ cho UI
        job.error = str(exc)
        job.meta["traceback"] = traceback.format_exc()
        job.touch(JobStatus.failed, f"Lỗi: {exc}")
        save_job(job, settings)
    finally:
        # Giữ artifacts; dọn upload tạm nếu có
        if video_path and video_path.exists():
            # giữ file trong thư mục job để truy vết
            dest = work / video_path.name
            if video_path.resolve() != dest.resolve():
                try:
                    shutil.copy2(video_path, dest)
                except OSError:
                    pass
