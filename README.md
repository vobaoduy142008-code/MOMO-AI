# Dyv10.1 — gói chuẩn bị đưa lên GitHub

Dyv10.1 = gộp **V4C** (bge-m3 + LoRA, train tiếp từ V4 của Trần) và **Dyv10.0** (phần Dyv học thêm tin SMS thật):
p = σ(0,6·logit p_V4C + 0,4·logit p_Dyv10.0), chuẩn hoá đầu vào và đọc thêm cuối tin dài như Dyv8.1/9.0.
Code, báo cáo và `ket_hop.json` đã ở trên GitHub, nhánh `dev2`. Thư mục này chỉ chứa thứ KHÔNG có trong git.

| Thư mục | Nội dung | Đưa lên GitHub? |
|---|---|---|
| `Dyv10.0/` | Model phần Dyv, bản **release**: train lại trên train + `val_vi` + `test_vi_internal` sau khi đã đo (như `--release` của Dyv6.0). `router.json` ghi `"release": true` | Chỉ qua **GitHub Release / Git LFS**, và chỉ sau khi Trần xác nhận giấy phép tin thật (QUESTION-54) |
| `v4c/` | Adapter LoRA V4C + calibrator (thay `bge_m3_lora_v4`) | Như trên |
| `du_lieu_mo_phong/` | Dữ liệu mô phỏng do nhóm sinh (data_v6, mục B, bộ 29 kiểu, danh sách 26 ca) — các file này đã có sẵn trong repo | Không cần (đã có trong `ml/sms_dataset/`) |
| `du_lieu_mo_phong/v8/` | **Bộ v8 (26/11/2026, mô phỏng):** `sms_v8_train.csv` (5.886 tin, dễ → siêu khó), `sms_v8_public_test.csv` (2.179 tin, gồm lại các bộ test cũ), thẻ dữ liệu `DATA_CARD.md`, bảng độ khó `do_kho.md`, `stats_v8.json`, bộ 60 kiểu gốc `vietnam_scam_dataset_60_kieu.csv` | Có (repo MOMO-AI đang để riêng tư) |
| `du_lieu_mo_phong/v8/private_KHONG_TRAIN/` | `sms_v8_private_test.csv` (828 tin, khó vượt trội) + `templates_v8_rieng.py` (mẫu để sinh lại bộ private). **Chỉ dùng để đo, không bao giờ train.** Không có trên kho công khai nbaphu08/Hallucination (QUESTION-58) | Được vì MOMO-AI riêng tư; nếu chuyển repo sang công khai thì bỏ thư mục này ra trước |
| `du_lieu_that_KHONG_UP/` | Tin SMS thật (kho của Trần, tin thành viên gửi) | **KHÔNG** — repo đang công khai, dữ liệu thật chỉ để trong `data/` (gitignore) |
| `ket_hop.json`, `report.md`, `test_26_ca.md` | Cấu hình gộp và kết quả đo | Đã có trong repo |
| `_to_delete/` | File tạm khi chép | Xoá đi |

Số đo trong `report.md` là của bản **trước release** (chưa thấy `val_vi`, `test_vi_internal`). Bản release đã học cả hai bộ đó
nên không còn tin SMS thật nào chưa học để đo lại; tạo lại bằng
`python ml/sms_dataset/train_dyv10.py --du-lieu-tran <kho của Trần>/data_processed/text --release`.

Cách đưa model lên (khi được phép): GitHub → repo → Releases → "Draft a new release" → tag `dyv10.1` → kéo thả
`Dyv10.0/Dyv10.0.joblib`, `Dyv10.0/Dyv10.0_router.joblib`, `v4c/adapter_model.safetensors`, `v4c/adapter_config.json`,
`v4c/calibrator.joblib` vào ô đính kèm → Publish. Người dùng tải về đặt vào `ml/sms_dataset/artifacts/Dyv10.0/` và
`ml/sms_dataset/chay_model_v4/v4c/`.
