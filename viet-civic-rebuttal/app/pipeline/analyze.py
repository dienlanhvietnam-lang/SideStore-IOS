from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from app.config import Settings
from app.models import AnalysisPayload
from app.pipeline.prompts import (
    DEMO_REBUTTAL_TEMPLATE,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
)


def _extract_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            raise
        return json.loads(match.group(0))


def analyze_with_llm(
    *,
    transcript: str,
    frame_notes: list[str],
    source_label: str,
    source_type: str,
    settings: Settings,
) -> AnalysisPayload:
    if not settings.has_llm:
        if not settings.allow_demo_mode:
            raise RuntimeError(
                "Chưa cấu hình OPENAI_API_KEY và chế độ demo đang tắt."
            )
        return _demo_analysis(transcript, frame_notes, source_label)

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
    user_prompt = USER_PROMPT_TEMPLATE.format(
        source_label=source_label or "không rõ",
        source_type=source_type,
        transcript=transcript.strip() or "(trống)",
        frame_notes="\n".join(frame_notes) if frame_notes else "(không có)",
    )
    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.4,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = response.choices[0].message.content or ""
    data = _extract_json(content)
    payload = AnalysisPayload.model_validate(data)
    payload.che_do = "llm"
    if not payload.phan_bien_van_xoi.strip():
        raise RuntimeError("Mô hình không trả về phần phản biện văn xuôi.")
    return payload


def _demo_analysis(
    transcript: str,
    frame_notes: list[str],
    source_label: str,
) -> AnalysisPayload:
    excerpt = (transcript or "").strip()
    if len(excerpt) > 280:
        excerpt = excerpt[:277] + "…"
    if not excerpt or excerpt.startswith("[Chưa có khóa"):
        excerpt = (
            "Chưa có transcript đầy đủ. Bản demo minh họa cấu trúc phản biện "
            "công dân dựa trên nguyên tắc kiểm chứng và văn xuôi chuẩn."
        )

    tom_tat = (
        f"Nguồn «{source_label or 'không tên'}» được đưa vào quy trình MVP. "
        f"Nội dung lời thoại/ghi chú hiện có: {excerpt}"
    )
    return AnalysisPayload(
        tom_tat_video=tom_tat,
        cac_khang_dinh=[
            "Video nêu một góc nhìn dư luận cần được tách thành sự kiện và ý kiến.",
            "Một số khẳng định có thể đang thiếu mốc thời gian, địa bàn hoặc nguồn.",
        ],
        lo_hong_lap_luan=[
            "Thiếu dẫn chứng có thể kiểm chứng công khai.",
            "Có nguy cơ khái quát hóa từ một trường hợp sang toàn bộ.",
            "Ngữ cảnh chính sách/pháp lý có thể chưa được nêu đủ.",
        ],
        diem_dung_can_thua_nhan=[
            "Việc người dân quan tâm và đặt câu hỏi về đời sống – chính sách là chính đáng.",
        ],
        canh_bao_rui_ro=[
            "Lan truyền nội dung thiếu nguồn có thể làm tăng hiểu nhầm trong cộng đồng.",
        ],
        gia_tri_cong_dan=(
            "Giúp người xem luyện thói quen kiểm chứng, phản biện ôn hòa và ưu tiên "
            "giải pháp hợp pháp có lợi cho cộng đồng."
        ),
        phan_bien_van_xoi=DEMO_REBUTTAL_TEMPLATE.strip(),
        goi_y_hanh_dong=[
            "Đối chiếu thông tin với nguồn chính thống trước khi chia sẻ.",
            "Ghi chú rõ phần đã kiểm được và phần còn nghi vấn.",
            "Nếu có kiến nghị, gửi qua kênh hợp pháp tới cơ quan có thẩm quyền.",
        ],
        do_tin_cay="thap",
        che_do="demo",
    )
