from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    port: int = 4321
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    openai_whisper_model: str = "whisper-1"
    allow_demo_mode: bool = True

    uploads_dir: Path = DATA / "uploads"
    jobs_dir: Path = DATA / "jobs"
    samples_dir: Path = DATA / "samples"

    @property
    def has_llm(self) -> bool:
        return bool(self.openai_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.jobs_dir.mkdir(parents=True, exist_ok=True)
    settings.samples_dir.mkdir(parents=True, exist_ok=True)
    return settings
