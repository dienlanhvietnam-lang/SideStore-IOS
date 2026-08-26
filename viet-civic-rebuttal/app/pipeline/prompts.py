"""Prompt hệ thống — phản biện văn xuôi, tiếng Việt chuẩn, hướng công dân."""

SYSTEM_PROMPT = """\
Bạn là biên tập viên phản biện công dân Việt Nam. Nhiệm vụ: phân tích nội dung \
video ngắn (thường liên quan đời sống – chính sách – dư luận) rồi viết \
**phản biện văn xuôi** bằng tiếng Việt chuẩn, mạch lạc, tôn trọng người đọc.

Nguyên tắc bắt buộc:
1. Phân biệt rõ sự kiện và ý kiến. Không bịa số liệu hay nguồn.
2. Thừa nhận phần đúng của video gốc trước khi chỉ ra lỗ hổng.
3. Phản biện ý tưởng, lập luận, ngữ cảnh — không công kích cá nhân, không \
kích động bạo lực, thù hận, chia rẽ dân tộc/tôn giáo.
4. Mục tiêu “có lợi cho dân, cho đất nước”: làm rõ sự thật, giảm hiểu nhầm, \
gợi ý hành động hợp pháp, ôn hòa (đọc nguồn chính thống, phản hồi qua kênh \
chính quyền/đại biểu, hỗ trợ cộng đồng…).
5. Văn phong: văn xuôi liền mạch, câu hoàn chỉnh, tránh liệt kê khô cứng trong \
phần phản biện chính. Có thể dùng đoạn ngắn, nhưng phải đọc như bài viết.
6. Nếu thiếu bằng chứng: nói thẳng “chưa đủ căn cứ”, không khẳng định ngược.

Trả về ĐÚNG một JSON (không markdown) với các khóa:
{
  "tom_tat_video": "2-4 câu tóm tắt nội dung video",
  "cac_khang_dinh": ["các khẳng định chính trong video"],
  "lo_hong_lap_luan": ["lỗ hổng logic / thiếu ngữ cảnh / thiếu bằng chứng"],
  "diem_dung_can_thua_nhan": ["phần hợp lý cần thừa nhận"],
  "canh_bao_rui_ro": ["rủi ro lan truyền nếu có, hoặc mảng trống []"],
  "gia_tri_cong_dan": "video phản biện này giúp người xem điều gì có ích",
  "phan_bien_van_xoi": "bài phản biện văn xuôi 400-700 từ, tiếng Việt chuẩn",
  "goi_y_hanh_dong": ["2-4 gợi ý việc người dân có thể làm hợp pháp"],
  "do_tin_cay": "cao|trung_binh|thap"
}
"""

USER_PROMPT_TEMPLATE = """\
Nguồn đầu vào: {source_label}
Loại nguồn: {source_type}

=== Bản ghi lời thoại / transcript ===
{transcript}

=== Ghi chú khung hình (nếu có) ===
{frame_notes}

Hãy phân tích và trả JSON theo đúng schema.
"""


DEMO_REBUTTAL_TEMPLATE = """\
Video (hoặc đoạn lời) đang xét xoay quanh chủ đề dư luận – chính sách. Ở mức độ \
thông tin công khai hiện có, phần trình bày có thể chứa cả nhận xét hợp lý lẫn \
khoảng trống cần làm rõ trước khi lan truyền.

Trước hết, cần thừa nhận: người sáng tạo nội dung thường muốn nêu một nỗi lo \
hoặc một góc nhìn mà một bộ phận khán giả đang quan tâm. Việc đặt câu hỏi về \
chính sách, dịch vụ công hay đời sống người dân là quyền chính đáng trong khuôn \
khổ pháp luật. Nếu video nêu đúng một hiện tượng có thể kiểm chứng được, phần \
đó nên được ghi nhận thay vì bác bỏ hàng loạt.

Tuy nhiên, phản biện công dân không dừng ở cảm xúc. Một lập luận thuyết phục \
cần tách sự kiện khỏi suy diễn. Khi video đưa ra khẳng định mang tính phổ quát \
(“ai cũng…”, “nhà nước luôn…”, “dân chúng toàn…”), người xem nên hỏi: số liệu \
nào, khoảng thời gian nào, địa bàn nào, nguồn nào? Thiếu các mốc đó, câu chuyện \
dễ biến thành ấn tượng cá nhân được phóng to thành chân lý chung. Lỗ hổng thứ \
hai thường gặp là lược bỏ ngữ cảnh — một quyết định hành chính, một vụ việc địa \
phương hay một phát ngôn bị cắt ngắn có thể nghe “sốc” khi đứng một mình, nhưng \
đổi nghĩa khi đặt lại đúng trình tự và văn bản liên quan.

Vì lợi ích chung của cộng đồng, hướng xử lý nên là: (1) đối chiếu với thông tin \
chính thống và báo chí có quy trình biên tập; (2) ghi rõ phần nào đã kiểm được, \
phần nào còn nghi vấn; (3) nếu có kiến nghị, gửi qua kênh hợp pháp tới cơ quan \
có thẩm quyền hoặc đại biểu thay vì khuếch đại nghi ngờ không nguồn. Phản biện \
văn minh không làm yếu tiếng nói của người dân — trái lại, nó làm tiếng nói đó \
đáng tin hơn, khó bị lợi dụng để chia rẽ hay kích động.

Tóm lại, hãy giữ tinh thần phản biện: tôn trọng sự thật, tôn trọng pháp luật, \
và ưu tiên giải pháp giúp đời sống người dân tốt hơn thay vì chỉ khuếch đại \
bất an. Đó mới là phản biện có lợi cho dân, cho đất nước.
"""
