from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from app.config import Settings


def transcribe_audio(audio_path: Path, settings: Settings) -> str:
    """Chuyển giọng nói thành chữ. Ưu tiên API Whisper khi có khóa."""
    if not settings.has_llm:
        return (
            "[Chưa có khóa API — không thể tự động nhận dạng giọng nói. "
            "Hãy dán bản ghi lời thoại thủ công hoặc cấu hình OPENAI_API_KEY.]"
        )

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
    with audio_path.open("rb") as f:
        result = client.audio.transcriptions.create(
            model=settings.openai_whisper_model,
            file=f,
            language="vi",
        )
    text = getattr(result, "text", None) or str(result)
    return (text or "").strip()
