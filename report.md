# Dyv10.1 — bản kết hợp V4C + Dyv10.0

Giữ phần V4C và cách gộp của Dyv9.0 (0,6 · logit V4C + 0,4 · logit Dyv, chuẩn hoá đầu vào, cửa sổ cuối), thay phần Dyv6.0 bằng **Dyv10.0**: cùng thuật toán Dyv6.0 nhưng học thêm 1.911 tin SMS thật (`train_vi_only`), độ phức tạp chọn bằng đường kiểm định trên `val_vi` (alpha = 1e-04, trọng số tin thật = 10; `../Dyv10.0/chon_cau_hinh.md`). Quyết định theo kế hoạch ghi trước `../Dyv10.0/ke_hoach.md`: **đạt cả năm điều kiện** (`../Dyv10.0/report.md`).

| | Dyv9.0 | **Dyv10.1** |
|---|---|---|
| Tin thật, nửa dev: độ chính xác · lừa đảo được cảnh báo · hợp lệ bị cảnh báo | 95.3% · 38/39 · 5/88 | **97.6%** · 38/39 · 2/88 |
| Tin thật, nửa giữ lại: độ chính xác · lừa đảo được cảnh báo · hợp lệ bị cảnh báo | 95.2% · 30/31 · 5/95 | **98.4%** · 30/31 · 1/95 |
| Hai nửa tin thật gộp: số tin sai | 12/253 | **5/253** (McNemar p = 0.016) |
| Tin thật, nửa dev, bỏ dấu: độ chính xác | 94.5% | 96.9% |
| Tin thật, nửa giữ lại, bỏ dấu: độ chính xác | 97.6% | 99.2% |
| 13 tin thật thành viên gửi: độ chính xác | 100.0% | 100.0% |
| Mục B, file test: độ chính xác | 83.4% | 82.6% |
| Bộ 29 kiểu, phần test: độ chính xác | 88.8% | 89.7% |
| Bộ 29 kiểu, phần test, bỏ dấu: độ chính xác | 89.2% | 88.9% |
| Danh sách 26 ca (tiêu chí riêng) | 15/22 | 16/22 |
| Mức độ học (`danh_gia_khop`): sai trên tin đã học → tin chưa học | 1.8% → 4.7% (overfitting nhẹ) | 0.4% → 2.0% (**khớp tốt**) |

Riêng phần Dyv trên hai nửa tin thật: Dyv6.0 sai 50/253, Dyv10.0 sai 8/253 (McNemar p = 5.1e-12) — lệch dữ liệu của phần Dyv gần như hết.

**Lưu ý:**

- "Khớp tốt" theo ngưỡng 2 điểm %: khoảng cách giữa tin đã học và tin chưa học là +1.6 điểm, khoảng tin cậy 95% từ +0.0 đến +3.5 — tập test chỉ 253 tin nên chưa chắc chắn. Đường học của phần Dyv (`../Dyv10.0/chon_cau_hinh.md`) cho thấy thêm tin SMS thật vẫn còn giúp.
- Hai nửa `test_vi_internal` đã được đo qua nhiều thử nghiệm trước (Dyv8.0 → Dyv9.0); `val_vi` đã dùng để chọn cấu hình nên không dùng để kết luận.
- Mục B (mô phỏng): 82.6% so với 83.4% — giảm nhẹ, trong mức luật cho (3 điểm). Nếu backend giữ V4 thay vì V4C (QUESTION-55): V4 + Dyv10.0 tốt hơn Dyv8.1 trên tin thật nhưng mục B giảm quá 3 điểm (`../Dyv10.0/report.md`).
- Phần Dyv10.0 học từ tin SMS thật của kho của Trần (nguồn, giấy phép: QUESTION-54). File model không commit, tạo lại bằng `train_dyv10.py` (cần kho của Trần); tin thật không lưu nội dung trong file model.
- Phần V4C như Dyv9.0: adapter chỉ ở máy thành viên AI/ML, backend vẫn chạy V4 (QUESTION-55).
