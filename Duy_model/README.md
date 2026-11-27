# Model Duy: model thống nhất kiểm tra tin nhắn lừa đảo

Thư mục này chứa **một model duy nhất**, hiện tại là **Dyv12.0.1**: code, dữ liệu, kết quả đo và file model. Model train từ đầu đến
cuối bằng **một lệnh** trên dữ liệu trong `du_lieu/`, không phụ thuộc model của người khác (V4/V4C), GPU hay dịch vụ ngoài. Mọi phiên
bản sau phát triển ngay trong thư mục này (xem "Phát triển phiên bản mới").

## Model làm gì

Nhận một tin nhắn hoặc đoạn hội thoại, trả về **% khả năng lừa đảo** và một trong 3 mức (D-20):

| % | Mức | Câu hiển thị |
|---|---|---|
| từ 70% | `lua_dao` | Lừa đảo — đừng chuyển tiền, đừng bấm link, đừng đọc mã OTP |
| 30–69% | `nghi_ngo` | Nghi ngờ — có dấu hiệu rủi ro, hãy kiểm tra lại qua kênh chính thức |
| dưới 30% | `hop_le` | Chưa thấy dấu hiệu rõ — vẫn cần cẩn trọng |

Không có mức "an toàn". Kèm theo là danh sách **dấu hiệu** đã thấy, ví dụ "đòi mã OTP/mật khẩu" hoặc "có link".

Cách hoạt động:

1. Chuẩn hoá tin: chữ đồng hình, ký tự ẩn, viết tắt, teencode.
2. Che link, số điện thoại và dãy số dài.
3. Tạo đặc trưng: TF-IDF từ 1–2 gram + ký tự 2–5 gram, cộng 30 cờ dấu hiệu.
4. Bộ phân loại SGD log-loss.
5. Hiệu chỉnh Platt để đổi điểm thành %.

File model chỉ **0,5 MB** và chạy trên CPU trong vài mili-giây.

## Kết quả (bản đo, đo một lần: `ket_qua/danh_gia_Dyv12.0.1.md`)

| Bộ | Dyv10.1 (V4C + Dyv10.0) | Dyv12.1 (V4C + Dyv12.0) | **Dyv12.0.1 (thống nhất)** |
|---|---|---|---|
| v8 public_test, đúng 3 mức | 76,0% | 80,1% | **82,6%** |
| v8 private_test, đúng 3 mức | 64,0% | 68,0% | **75,1%** |
| v8 private_test, cảnh báo đúng (mốc 30%) | 79,8% | 83,2% | **87,1%** |
| Mục B, file test (mốc 30%) | 82,6% | 87,4% | **92,9%** |
| Bộ 29 kiểu, đúng 3 mức | 73,0% | 77,4% | 75,1% |
| 253 tin SMS thật, số tin sai | 5 | 6 | **10** (9 tin hợp lệ bị báo nhầm, 1 tin lừa đảo bị bỏ lỡ) |

**Bias / variance** (mốc 30%):

- **Bias** (sai trên tin SMS thật đã học): 0,1%.
- **Variance**: +3,8 điểm. Theo ngưỡng 2 điểm, đây là overfitting trên tin SMS thật.
- **Lệch dữ liệu**: +5,1 điểm ở public (câu mới), +9,0 điểm ở private.

**Điểm yếu chính** là báo nhầm tin SMS thật hợp lệ, dù ROC-AUC trên tin thật vẫn 0,99. Model xếp hạng tin đúng, nhưng mốc 30% đang hơi
thấp với tin thật. Đây là việc của phiên bản sau, chọn cách sửa trên `val_vi`.

Bộ mục B, 29 kiểu và v8 là tin mô phỏng: số trên các bộ này chỉ để so giữa các phiên bản, không phải độ chính xác ngoài đời.

## Cấu trúc

```
Duy_model/
  duy_model/          code của model (xu_ly.py: xử lý tin; mo_hinh.py: MoHinhDuy; du_lieu.py: đọc dữ liệu)
  du_lieu/
    that/             tin SMS thật (train_vi_only, val_vi, test_vi_internal) — nguồn và giấy phép ở mục Dữ liệu
    mo_phong/         data_v6, bộ 29 kiểu, mục B (train / test)
    v8/               sms_v8_train.csv, sms_v8_public_test.csv, DATA_CARD.md
      private_KHONG_TRAIN/sms_v8_private_test.csv   chỉ để đo, KHÔNG BAO GIỜ train
  mo_hinh/<phiên bản>/  ban_do.joblib (để đo), model.joblib (release, dùng cho web), cau_hinh.json, oof_v8_train.csv
  ket_qua/            danh_gia_<phiên bản>.md/.json, kiem_tra_du_lieu_v8.md
  train.py  danh_gia.py  kiem_tra_du_lieu.py  du_doan.py  api.py
  PHIEN_BAN.md        nhật ký phiên bản
```

## Cách dùng

```bash
pip install -r requirements.txt

python du_doan.py "Tài khoản của bạn bị khoá, bấm link để xác minh"   # thử nhanh
uvicorn api:app --port 8001                                             # chạy API

python kiem_tra_du_lieu.py               # kiểm chất lượng bộ v8
python train.py                          # chọn cấu hình + train bản đo (khoảng 3 phút)
python danh_gia.py                       # đo bản đo một lần trên các bộ test
python train.py --release                # train bản release (thêm val_vi + test_vi_internal) -> model.joblib
```

API:

- `POST /kiem-tra` với body `{"van_ban": "..."}` trả về `{"phan_tram": 87, "muc": "lua_dao", "ket_luan": "...", "dau_hieu": [...], "phien_ban": "Dyv12.0.1"}`.
- `GET /suc-khoe` để kiểm tra API còn chạy.

API không lưu tin người dùng gửi.

**Đưa vào trang web** (backend FastAPI + frontend), chọn một trong hai cách:

1. **Gọi API này** từ backend: chạy `api.py` như một service riêng; backend gửi tin đã nhận tới `POST /kiem-tra`.
2. **Nhúng thẳng vào backend Python:** chép thư mục `duy_model/` và file `model.joblib` vào backend, rồi gọi:

   ```python
   from duy_model.mo_hinh import MoHinhDuy
   m = MoHinhDuy.nap("model.joblib")
   m.du_doan(tin_nhan)
   ```

   Chỉ cần numpy, scipy, scikit-learn và joblib, đủ nhẹ cho Vercel Function.

**Lưu ý khi gửi tiếp tin cho LLM:** nếu trang web gửi tin tiếp cho LLM (ví dụ Gemini) để viết lời giải thích, phải che số điện thoại và
số tài khoản trước. BTC và dự án đều yêu cầu điều này.

## Phát triển phiên bản mới (từ Dyv12.0.1 trở đi)

1. Sửa code trong `duy_model/` và/hoặc thêm dữ liệu vào `du_lieu/` (dữ liệu mới phải ghi nguồn, giấy phép, phạm vi, căn cứ vào mục
   Dữ liệu bên dưới).
2. Đặt tên phiên bản mới, ví dụ `Dyv12.0.2`. Ghi **trước khi train** vào `PHIEN_BAN.md`: định thay đổi gì và thế nào là "tốt hơn".
3. `python train.py --phien-ban Dyv12.0.2`: cấu hình chỉ chọn trên tập val (`val_vi` + out-of-fold của tệp train v8).
4. `python danh_gia.py --phien-ban Dyv12.0.2`: đo **một lần**, so với phiên bản trước. Không chỉnh model theo kết quả test.
5. Nếu đạt: `python train.py --phien-ban Dyv12.0.2 --release`, đổi `DUY_MODEL_PHIEN_BAN` của API, ghi kết quả vào `PHIEN_BAN.md`.
6. Commit và push lên repo `vobaoduy142008-code/MOMO-AI`.

Luật cố định:

- **Không bao giờ train trên `private_KHONG_TRAIN/`.** Ngoài ra không lựa chọn nào được dùng public_test hay private_test.

## Dữ liệu: nguồn, giấy phép, phạm vi, căn cứ (Điều 11, 12, 28 thể lệ; phản hồi BTC 27/11/2026)

| Dữ liệu | Nguồn | Giấy phép | Phạm vi | Căn cứ |
|---|---|---|---|---|
| `du_lieu/that/` (2.547 tin SMS thật) | Vietnamese Quality-Assured SMS Scam Dataset, Tran Nguyen Thai Tuan, Le Hoang Khang, Nguyen Minh Tai, Nguyen Van Thang, Mai Hoang Dinh (2026), github.com/trannguyenthaituan251209/vietnamese_sms_dataset. Đội dùng bản đã khử trùng và chia lại của thành viên Trần. | **CC BY 4.0** (ghi công tác giả; đội đã sửa đổi: bỏ trùng, chia lại train/val/test) | Train và đo | Dữ liệu công khai có giấy phép; tác giả ghi có sự đồng ý của người đóng góp; đã ẩn danh bằng token `[PHONE]`, `[MONEY]`… |
| `du_lieu/mo_phong/`, `du_lieu/v8/` | Đội tạo trong thời gian thi, cùng Claude (Anthropic) | Của đội | Train và đo | Do đội tạo, không phải dữ liệu cá nhân: số điện thoại, số tài khoản, link, tên đều giả; tên ngân hàng và ví chỉ để mô phỏng tin giả mạo |

Chưa rõ nguồn: khung 29 kiểu và bộ 60 kiểu do thành viên gửi; 60 câu mẫu gốc của bộ 60 kiểu nằm nguyên văn trong
`sms_v8_public_test.csv`.

Kiểm tra chất lượng bộ v8 (`ket_qua/kiem_tra_du_lieu_v8.md`):

- **Cấu trúc:** đủ cột, không có tin trống hay nhãn lạ.
- **Rò rỉ:** không có câu, mẫu câu hay câu gần giống (cosine ≥ 0,9) chung giữa train và hai tệp test.
- **Dữ liệu cá nhân:** không có số điện thoại nào ngoài dải giả.
- **Trùng lặp:** public_test có 7 câu trùng nhau trong chính tệp, đều đến từ các bộ test cũ.

**Công cụ AI đã dùng:** code, dữ liệu mô phỏng và tài liệu trong thư mục được viết cùng **Claude** (Anthropic) qua Claude Code. Model
không gọi LLM nào khi chạy.
