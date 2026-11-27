# Nhật ký phiên bản: model Duy

Mỗi phiên bản ghi theo thứ tự sau:

1. Trước khi train: định thay đổi gì và thế nào là "tốt hơn".
2. Sau khi đo (một lần): kết quả và kết luận.

Mỗi phiên bản là một thư mục `mo_hinh/<tên>/` và một báo cáo `ket_qua/danh_gia_<tên>.md`.

## Dyv12.0.1 (27/11/2026): model thống nhất đầu tiên

**Thay đổi:**

- Gom phần Dyv của Dyv12.1 thành một model đứng riêng (`MoHinhDuy`) và bỏ phần V4C.
  - Lý do bỏ: V4C train tiếp từ V4 của thành viên khác, cần GPU, và có thể mang dữ liệu chưa rõ giấy phép (QUESTION-60).
- Code gọn lại trong `duy_model/`.
- Train bằng một lệnh. File model 0,5 MB, chạy trên CPU.

**Dữ liệu train:** 24.776 dòng, gồm:

- `data_v6`: 12.455 tin;
- tin SMS thật `train_vi_only`: 1.911 tin;
- mục B, phần train: 1.069 tin;
- bộ 29 kiểu, phần train: 2.069 tin;
- bộ v8, tệp train: 5.886 tin.

Tin nghi ngờ học bằng nhãn mềm 0,5.

**Cấu hình** (chọn trên val, không nhìn test): alpha 1e-5, trọng số tin thật 10.

- PR-AUC `val_vi`: 0,962.
- PR-AUC out-of-fold trên tệp train v8: 0,978.
- Trùng khớp với lựa chọn của Dyv12.0, vì cùng đặc trưng và cùng dữ liệu.

**Kết quả** (`ket_qua/danh_gia_Dyv12.0.1.md`, so với Dyv12.1):

| Bộ | Dyv12.1 | Dyv12.0.1 |
|---|---|---|
| v8 public, đúng 3 mức | 80,1% | 82,6% |
| v8 private, đúng 3 mức | 68,0% | 75,1% |
| v8 private, mốc 30% | 83,2% | 87,1% |
| Mục B (mốc 30%) | 87,4% | 92,9% |
| Bộ 29 kiểu, đúng 3 mức | 77,4% | 75,1% |
| 253 tin SMS thật, số tin sai | 6 | **10** (9 báo nhầm) |

**Bias / variance trên tin SMS thật:** bias 0,1%, variance +3,8 điểm (overfitting).

**Lệch dữ liệu:** +5,1 điểm (public câu mới), +9,0 điểm (private).

**Bản release** (`model.joblib`): train lại cùng cấu hình, thêm `val_vi` và `test_vi_internal` (25.412 dòng). Đây là bản dùng cho API.

**Việc tiếp theo** (Dyv12.0.2, chọn trên `val_vi`): giảm báo nhầm tin SMS thật hợp lệ. ROC-AUC trên tin thật đã 0,99, nên model xếp
hạng tốt; lỗi nằm ở hiệu chỉnh %. Hướng thử: hiệu chỉnh riêng cho tin thật, hoặc tăng trọng số tin thật trong bước hiệu chỉnh.
