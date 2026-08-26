# Phản biện công dân (MVP)

Ứng dụng web tiếng Việt để **phân tích video ngắn** (TikTok/reel/upload) và **soạn phản biện văn xuôi** theo hướng kiểm chứng, ôn hòa, có lợi cho dân và đất nước.

- Cổng giao diện: **http://0.0.0.0:4321**
- Ngôn ngữ UI + đầu ra: **tiếng Việt chuẩn**
- Đầu ra chính MVP: **phản biện văn xuôi** (có thể chỉnh sửa / sao chép trước khi đăng)

## Chạy nhanh

```bash
cd viet-civic-rebuttal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # thêm OPENAI_API_KEY nếu có
python run.py
```

Mở trình duyệt: [http://127.0.0.1:4321](http://127.0.0.1:4321)

Không có khóa API vẫn chạy được **chế độ demo** (văn xuôi mẫu + khung phân tích).

## Cách dùng

1. Tải video lên, **hoặc** dán URL (yt-dlp), **hoặc** chỉ dán bản ghi lời thoại.
2. Bấm **Phân tích & soạn phản biện**.
3. Theo dõi tiến trình trên trang việc.
4. Đọc tóm tắt / lỗ hổng / giá trị công dân; chỉnh **phản biện văn xuôi**; sao chép khi đạt.

## Pipeline MVP

```text
Nguồn (upload | URL | transcript)
  → ffmpeg tách audio + khung hình
  → Whisper API (nếu có khóa) nhận dạng tiếng Việt
  → LLM soạn JSON phân tích + phản biện văn xuôi
  → UI duyệt / sửa / sao chép
```

## Nguyên tắc “có lợi cho dân”

Được khóa trong prompt hệ thống:

- Thừa nhận phần đúng trước khi chỉ lỗi
- Không bịa nguồn / số liệu
- Phản biện ý tưởng, không công kích cá nhân
- Không kích động bạo lực / thù hận
- Gợi ý hành động hợp pháp, ôn hòa
- Người biên tập chịu trách nhiệm trước khi đăng

## Cấu trúc thư mục

```text
viet-civic-rebuttal/
  app/
    main.py              # FastAPI + UI
    config.py
    models.py
    pipeline/            # media, ASR, phân tích
    templates/           # giao diện Jinja tiếng Việt
    static/
  data/uploads|jobs|samples
  run.py                 # chạy cổng 4321
```

## Hướng mở rộng (đã phác trong UI)

1. Vision LLM đọc chữ trên khung hình
2. RAG nguồn pháp luật / số liệu chính thống
3. Dựng short 9:16 (TTS + phụ đề) từ văn đã duyệt
4. Hàng đợi nhiều biên tập viên, nhật ký xuất bản

## Lưu ý pháp lý

- Tôn trọng điều khoản nền tảng khi tải URL; ưu tiên nội dung bạn có quyền dùng
- Không deepfake mặt/giọng người thật
- Không vận hành mạng tài khoản giả để tung tin
