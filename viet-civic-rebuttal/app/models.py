from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    queued = "queued"
    downloading = "downloading"
    extracting = "extracting"
    transcribing = "transcribing"
    analyzing = "analyzing"
    done = "done"
    failed = "failed"


class JobCreateResponse(BaseModel):
    job_id: str
    message: str


class AnalysisPayload(BaseModel):
    tom_tat_video: str = ""
    cac_khang_dinh: list[str] = Field(default_factory=list)
    lo_hong_lap_luan: list[str] = Field(default_factory=list)
    diem_dung_can_thua_nhan: list[str] = Field(default_factory=list)
    canh_bao_rui_ro: list[str] = Field(default_factory=list)
    gia_tri_cong_dan: str = ""
    phan_bien_van_xoi: str = ""
    goi_y_hanh_dong: list[str] = Field(default_factory=list)
    do_tin_cay: str = "trung_binh"
    che_do: str = "llm"  # llm | demo


class JobRecord(BaseModel):
    id: str
    status: JobStatus = JobStatus.queued
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    source_type: str = "upload"  # upload | url | transcript
    source_label: str = ""
    progress_message: str = "Đang chờ xử lý…"
    error: Optional[str] = None
    transcript: str = ""
    frame_notes: list[str] = Field(default_factory=list)
    analysis: Optional[AnalysisPayload] = None
    meta: dict[str, Any] = Field(default_factory=dict)

    def touch(self, status: JobStatus | None = None, message: str | None = None) -> None:
        if status is not None:
            self.status = status
        if message is not None:
            self.progress_message = message
        self.updated_at = datetime.now(timezone.utc).isoformat()
