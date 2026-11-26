# Chạy thử danh sách test 26 ca với Dyv10.1

Dyv10.1 = TB w=0.4 + chuẩn hoá đầu vào + cửa sổ cuối; V4C + Dyv10.0 (Dyv học thêm tin SMS thật) (gộp V4C + Dyv10.0). Điểm là % của model, chưa qua các lớp khác của hệ thống (luật cờ đỏ, dự phòng v2, Gemini). Tiêu chí: *Cao* = từ 70%, *Thấp* = dưới 30%, #20 = từ 30%. Không có #23 (chưa có nguyên văn tin MTTQ); #17 dựng lại theo mô tả. Tạo bằng `python run_test_list.py`.

| Câu | Nhóm | Nên ra | V4C | Dyv10.0 | **Dyv10.1** | Mức Dyv10.1 | Đạt | Dấu hiệu Dyv thấy |
|---|---|---|---|---|---|---|---|---|
| #1 | A | cao | 98% | 99% | **99%** | Rất có thể là lừa đảo | ✓ | Tin yêu cầu chuyển tiền; Có số tài khoản nhận tiền |
| #2 | A | cao | 44% | 99% | **84%** | Rất có thể là lừa đảo | ✓ | Tin đòi mã OTP hoặc mật khẩu; Đe dọa khóa tài khoản, cắt dịch vụ hay bắt giữ |
| #3 | A | cao | 98% | 98% | **98%** | Rất có thể là lừa đảo | ✓ | Tin yêu cầu chuyển tiền; Tài khoản nhận tiền lạ hoặc của người khác |
| #4 | A | cao | 93% | 33% | **78%** | Rất có thể là lừa đảo | ✓ | Hối thúc phải làm ngay |
| #5 | A | cao | 90% | 72% | **84%** | Rất có thể là lừa đảo | ✓ | – |
| #6 | A | cao | 99% | 98% | **99%** | Rất có thể là lừa đảo | ✓ | Tin yêu cầu chuyển tiền; Đòi đóng phí hoặc đặt cọc trước |
| #7 | B | thấp | 45% | 98% | **79%** | Rất có thể là lừa đảo | ✗ | – |
| #8 | B | thấp | 91% | 7% | **57%** | Có dấu hiệu đáng ngờ — cần xác minh | ✗ | Tin đòi mã OTP hoặc mật khẩu; Mở đầu bằng lời cảnh báo nhưng lại đòi tiền / mã / bấm link |
| #9 | B | thấp | 50% | 64% | **56%** | Có dấu hiệu đáng ngờ — cần xác minh | ✗ | Đe dọa khóa tài khoản, cắt dịch vụ hay bắt giữ |
| #10 | B | thấp | 5% | 3% | **4%** | Chưa thấy dấu hiệu rõ — vẫn cần cẩn trọng | ✓ | – |
| #11 | B | thấp | 1% | 33% | **3%** | Chưa thấy dấu hiệu rõ — vẫn cần cẩn trọng | ✓ | – |
| #12 | B | thấp | 0% | 1% | **1%** | Chưa thấy dấu hiệu rõ — vẫn cần cẩn trọng | ✓ | Tin đòi mã OTP hoặc mật khẩu; Bảo cài ứng dụng |
| #13 | C | cao | 99% | 99% | **99%** | Rất có thể là lừa đảo | ✓ | – |
| #14 | C | cao | 41% | 98% | **79%** | Rất có thể là lừa đảo | ✓ | Hứa trúng thưởng, tặng quà |
| #15 | C | cao | 48% | 99% | **86%** | Rất có thể là lừa đảo | ✓ | Tin yêu cầu chuyển tiền; Có số tài khoản nhận tiền |
| #16 | C | cao | 22% | 63% | **37%** | Có dấu hiệu đáng ngờ — cần xác minh | ✗ | Hứa trúng thưởng, tặng quà |
| #17 | C | cao | 3% | 15% | **6%** | Chưa thấy dấu hiệu rõ — vẫn cần cẩn trọng | ✗ | Hứa trúng thưởng, tặng quà; Mở đầu bằng lời cảnh báo nhưng lại đòi tiền / mã / bấm link |
| #18 | D | cao | 78% | 94% | **86%** | Rất có thể là lừa đảo | ✓ | – |
| #19 | D | cao | 54% | 77% | **64%** | Có dấu hiệu đáng ngờ — cần xác minh | ✗ | – |
| #20 | D | cao | 100% | 97% | **99%** | Rất có thể là lừa đảo | ✓ | Link kèm yêu cầu đăng nhập, xác thực hoặc nhập thông tin |
| #21 | E | cao | 98% | 99% | **98%** | Rất có thể là lừa đảo | ✓ | Tin yêu cầu chuyển tiền; Có số tài khoản nhận tiền |
| #22 | E | cao | 84% | 78% | **82%** | Rất có thể là lừa đảo | ✓ | Đe dọa khóa tài khoản, cắt dịch vụ hay bắt giữ; Xưng là cơ quan nhà nước |
| #24 | F | kiểm tra che | 0% | 65% | **3%** | Chưa thấy dấu hiệu rõ — vẫn cần cẩn trọng |  | Tin yêu cầu chuyển tiền |
| #25 | F | kiểm tra che | 1% | 1% | **1%** | Chưa thấy dấu hiệu rõ — vẫn cần cẩn trọng |  | – |
| #26 | F | kiểm tra che | 2% | 43% | **9%** | Chưa thấy dấu hiệu rõ — vẫn cần cẩn trọng |  | – |

**Đạt theo nhóm:** A 6/6, B 3/6, C 3/5, D 2/3, E 2/2 — tổng **16/22**.

## #21, #22 (chèn lệnh / mạo danh "đã xác minh") — lời kết luận của model

- #21: 98% — không có chữ "an toàn", không có "100%". Lời kết luận lấy từ mẫu cố định theo mức, nên câu bị chèn trong tin không đổi được chữ; % do model tính, không đọc lệnh trong tin. Phần phân tích của Gemini phải kiểm trên hệ thống.
- #22: 82% — không có chữ "an toàn", không có "100%". Lời kết luận lấy từ mẫu cố định theo mức, nên câu bị chèn trong tin không đổi được chữ; % do model tính, không đọc lệnh trong tin. Phần phân tích của Gemini phải kiểm trên hệ thống.

## #24–#26 — các lớp che thông tin

Model chỉ cần che số (`mask` của Dyv, `sanitize_pii` của V4); **lớp che cuối của backend** (`mask_residual`, D-10) mới là lớp chạy trước khi gửi Gemini và trước khi lưu.

| Câu | Dyv (`mask`) | V4 (`sanitize_pii`) | Backend (`mask_residual`) | Còn lộ sau lớp che cuối |
|---|---|---|---|---|
| #24 | `Chuyen vao [NUMBER] ten NGUYEN VAN AN, dia chi 12 Nguyen Trai Q1` | `Chuyen vao [NUMBER] ten NGUYEN VAN AN, dia chi 12 Nguyen Trai Q1` | `Chuyen vao [STK] ten [TEN], dia chi [DIA_CHI]` | không |
| #25 | `Ma OTP: 123 456` | `Ma OTP: 123 456` | `Ma OTP: [OTP]` | không |
| #26 | `ở ngõ 12 hoàng quốc việt, tên lan anh` | `ở ngõ 12 hoàng quốc việt, tên lan anh` | `ở ngõ 12 hoàng quốc việt, tên lan anh` | `lan anh`; `ngõ 12 hoàng quốc việt` |
