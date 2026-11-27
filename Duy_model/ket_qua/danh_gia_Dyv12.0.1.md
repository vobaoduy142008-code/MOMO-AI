# Dyv12.0.1: kết quả đo (bản đo, một lần)

Tạo bằng `python danh_gia.py`. Dyv10.1 và Dyv12.1 là bản gộp V4C + Dyv cũ (bản đo), cùng các bộ test. Bộ mục B, 29 kiểu, v8 là tin mô phỏng: chỉ để so giữa các bản, không phải độ chính xác thật.

| Bộ | n | Mốc 30%: Dyv10.1 / Dyv12.1 / **Dyv12.0.1** | 3 mức: Dyv10.1 / Dyv12.1 / **Dyv12.0.1** | Bắt lừa đảo (Dyv12.0.1) | Nhầm hợp lệ (Dyv12.0.1) | ROC-AUC (Dyv12.0.1) |
|---|---|---|---|---|---|---|
| Tin thật, nửa dev | 127 | 97.6% / 97.6% / **95.3%** | 95.3% / 95.3% / **92.1%** | 39/39 | 6/88 | 0.996 |
| Tin thật, nửa giữ lại | 126 | 98.4% / 97.6% / **96.8%** | 98.4% / 97.6% / **95.2%** | 30/31 | 3/95 | 0.992 |
| Mục B, file test | 253 | 82.6% / 87.4% / **92.9%** | 82.6% / 86.2% / **92.5%** | 60/72 | 6/181 | 0.905 |
| Bộ 29 kiểu, phần test | 571 | 89.7% / 92.3% / **89.1%** | 73.0% / 77.4% / **75.1%** | 341/391 | 12/180 | 0.987 |
| v8 public_test | 2179 | 87.4% / 90.2% / **90.8%** | 76.0% / 80.1% / **82.6%** | 1083/1200 | 83/979 | 0.976 |
| v8 private_test | 828 | 79.8% / 83.2% / **87.1%** | 64.0% / 68.0% / **75.1%** | 377/440 | 44/388 | 0.941 |

Tin SMS thật, gộp hai nửa (253 tin): sai Dyv10.1 5, Dyv12.1 6, **Dyv12.0.1 10**.

## Bias / variance (mốc 30%)

- **Bias** (sai trên 1911 tin SMS thật đã học): **0.1%**
- **Variance** (tin SMS thật chưa học sai thêm): **+3.8 điểm** (sai 4.0%)
- **Lệch dữ liệu**: v8 public câu mới +5.1 điểm (sai 9.1%), v8 private +9.0 điểm (sai 12.9%)
- Tệp train v8, out-of-fold chia theo mẫu (mẫu câu chưa học): sai 11.7%
