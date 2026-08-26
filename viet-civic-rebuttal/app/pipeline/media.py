from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


def run_cmd(args: list[str], timeout: int = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def download_url(url: str, out_dir: Path) -> Path:
    """Tải video từ URL bằng yt-dlp (best effort)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    template = str(out_dir / "%(id)s.%(ext)s")
    run_cmd(
        [
            "yt-dlp",
            "--no-playlist",
            "-f",
            "bv*[height<=1080]+ba/b[height<=1080]/b",
            "-o",
            template,
            "--merge-output-format",
            "mp4",
            url,
        ],
        timeout=900,
    )
    videos = sorted(
        list(out_dir.glob("*.mp4"))
        + list(out_dir.glob("*.webm"))
        + list(out_dir.glob("*.mkv")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not videos:
        raise RuntimeError("Không tìm thấy file video sau khi tải URL.")
    return videos[0]


def extract_audio(video_path: Path, audio_path: Path) -> Path:
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    run_cmd(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(audio_path),
        ]
    )
    return audio_path


def sample_frames(video_path: Path, frames_dir: Path, fps: float = 0.5) -> list[Path]:
    """Lấy khung hình thưa để hỗ trợ mô tả ngữ cảnh."""
    frames_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(frames_dir / "frame_%03d.jpg")
    run_cmd(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vf",
            f"fps={fps}",
            "-q:v",
            "5",
            pattern,
        ]
    )
    frames = sorted(frames_dir.glob("frame_*.jpg"))
    # Giới hạn để MVP nhẹ
    return frames[:12]


def describe_frames_heuristic(frames: list[Path]) -> list[str]:
    """Ghi chú khung hình không dùng vision model (MVP)."""
    notes: list[str] = []
    for i, frame in enumerate(frames, start=1):
        size_kb = max(1, frame.stat().st_size // 1024)
        notes.append(
            f"Khung {i}/{len(frames)}: đã trích ({frame.name}, ~{size_kb}KB). "
            "Cần đối chiếu chữ/overlay trên màn hình khi xem lại video gốc."
        )
    if not notes:
        notes.append("Không trích được khung hình — phân tích chủ yếu dựa trên lời thoại.")
    return notes


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sanitize_filename(name: str) -> str:
    name = Path(name).name
    name = re.sub(r"[^\w.\-()+ ]+", "_", name, flags=re.UNICODE)
    return name[:180] or "video.bin"
