# Thẻ dữ liệu — bộ v8: train / public_test / private_test (3 mức lừa đảo / nghi ngờ / hợp lệ)

> **Đây là dữ liệu TỔNG HỢP (mô phỏng) do AI viết mẫu, KHÔNG phải tin nhắn thật.** Số điện thoại, số tài khoản, link, tên người
> trong cột `text_raw` đều là giả — **không gọi, không bấm thử**. Tổng đài ngân hàng trong tin hợp lệ là số công khai của ngân hàng.
> Đưa tin trong bộ này lên giao diện demo thì phải gắn nhãn "mô phỏng" (AGENTS.md luật 3). Mức `hop_le` nghĩa là "chưa thấy dấu hiệu
> rõ", **không bao giờ** là "an toàn" (luật 4).

## Ba tệp

| Tệp | Số tin | Dùng để | Có trong kho git? |
|---|---|---|---|
| `sms_v8_train.csv` | **5.886** | Train: từ dễ tới siêu khó, 66 chủ đề | Có |
| `sms_v8_public_test.csv` | **2.179** | Đo công khai: dễ hơn, nhiều câu hơn; gồm lại các bộ test cũ + câu mới, có câu thuộc chủ đề train chưa từng có | Có |
| `sms_v8_private_test.csv` | **828** | Đo kín: khó vượt trội, định dạng và cách biến đổi chữ không có ở train, 11 chủ đề train không có | **Không** — kho của đội công khai; mẫu sinh ra nó ở `templates_v8_rieng.py` cũng không commit (QUESTION-58). Người phụ trách dữ liệu gửi riêng khi cần đo |

Nhãn 3 mức là **đề xuất** (DECISION-01 chưa chốt bộ nhãn, QUESTION-43). Không dùng số đo trên bộ này để báo cáo độ chính xác của sản
phẩm: độ chính xác thật phải đo trên tin thật (`../MODEL_VERSIONS.md`).

## Ba mức và bốn độ khó

| `nhan` | Nghĩa | Model nên cho | `muc_tieu` |
|---|---|---|---|
| `lua_dao` | Có yêu cầu gây hại (chuyển tiền vào tài khoản cá nhân/lạ, đưa OTP/mật khẩu/số thẻ/ảnh CCCD cầm tay, cài app từ link/.apk, đăng nhập qua link không chính thức, đóng phí để được nhận...) hoặc đúng một kịch bản lừa đã biết | ≥ 70% "Rất có thể là lừa đảo" | 1 |
| `nghi_ngo` | Bối cảnh có thể thật, chưa có yêu cầu gây hại rõ, nhưng có điểm phải tự xác minh | 30–69% "Có dấu hiệu đáng ngờ — cần xác minh" | 0,5 |
| `hop_le` | Không có yêu cầu gây hại, dù có chữ "khóa", "OTP", "công an", "chuyển tiền", "bắt cóc"... | < 30% "Chưa thấy dấu hiệu rõ — vẫn cần cẩn trọng" | 0 |

**Độ khó** (`muc_do`): `de` — lộ nhiều dấu hiệu; `trung_binh` — ít dấu hiệu, lời lẽ lịch sự; `kho` — bắt chước định dạng tin thật, chỉ còn
một dấu hiệu nhỏ, hoặc hội thoại nhiều lượt; `sieu_kho` — không có từ khóa quen (không link, không "OTP", không "chuyển khoản"), dùng
đúng tên cơ quan mới, mượn quan hệ quen biết, giai đoạn mồi chưa đòi tiền, hoặc tin hợp lệ dày đặc từ khóa lừa đảo (cảnh báo, người kể
lại vụ bị lừa). Tin lừa đảo/nghi ngờ bị biến đổi chữ (trừ chỉ thêm emoji) được nâng một độ khó. `khong_ro` = bộ test cũ không ghi độ khó.

## Thành phần

| | train | public_test | private_test |
|---|---|---|---|
| Lừa đảo · nghi ngờ · hợp lệ | 2.936 · 902 · 2.048 | 1.017 · 183 · 979 | 397 · 43 · 388 |
| Dễ · trung bình · khó · siêu khó | 1.180 · 2.798 · 1.428 · 480 | 85 · 1.316 · 643 · 13 (+ 122 không rõ) | 0 · 0 · 58 · 770 |
| Số mẫu (template) | 285 | 145 mẫu mới + 60 câu gốc + 976 tin test cũ | 177 |
| Số chủ đề | 66 | 146 (kể cả chủ đề của test cũ) | 77 |
| Tin thuộc chủ đề train không có | 0 | 54 | 171 |
| Hội thoại nhiều lượt | 368 (+ 96 lời gọi một lượt) | 16 (+ 70) | 81 |
| Tin có biến đổi chữ | 1.771 | 177 | 412 |
| Kênh | Zalo 1.757 · SMS 1.724 · Facebook 936 · Messenger 573 · email 480 · gọi 248 · Telegram 144 · TikTok 24 | SMS 941 · Zalo 483 · email 224 · khác 153 · Messenger 120 · Facebook 114 · gọi 78 · TikTok 40 · Telegram 26 | Zalo 270 · SMS 185 · email 130 · Messenger 116 · Facebook 70 · Telegram 33 · gọi 24 |

Tỉ lệ tin không dấu gần bằng nhau giữa 3 nhãn trong mỗi tệp (train 44–48%, public 36–48%, private 35–45%), để "không dấu" không thành
dấu hiệu của một nhãn.

**public_test gồm:** 571 tin test của `data_v7` (bộ 29 kiểu), 253 tin test mục B (`data_hard_negatives`), 25 câu `test_suite/cau_test_26.csv`
(cao → lừa đảo, kiểm tra → nghi ngờ, thấp → hợp lệ), 127 câu `test_suite/cases*.py` (1 → lừa đảo, 0 → hợp lệ), **60 câu mẫu gốc**
(`sample_script`) của bộ 60 kiểu, và 1.143 tin mới từ 145 mẫu public.

## Chủ đề

- **Bộ 60 kiểu** (`nguon/vietnam_scam_dataset.csv`, thành viên gửi ngày 26/11/2026; nguồn gốc của tệp chưa rõ — QUESTION-58): 7 nhóm, từ
  giả danh công an, thuế, BHXH... tới deepfake, mã QR độc, dàn cảnh va chạm. 29 kiểu đầu khớp 29 kiểu cũ (`kieu_lua` 1–29 của
  `templates_v7.KIEU_LUA`), 31 kiểu còn lại mới. Mẫu train/private **không** diễn đạt lại câu gốc — câu gốc chỉ nằm ở public_test.
  **6 kiểu không có mẫu train** (để đo khả năng gặp kiểu chưa học): t08 Tòa án/Viện kiểm sát, t21 xóa nợ xấu CIC, t37 tuyển mẫu ảnh nhí,
  t52 trạm BTS giả, t53 phần mềm điều khiển từ xa, t58 bảo hiểm nhân thọ.
- **11 chủ đề mới từ research** (có ở cả 3 tệp): bắt cóc online, đổi tiền mới dịp Tết, đổi ngoại tệ/kiều hối, mua vàng & đầu tư vàng,
  trao đổi đồ cũ, mua vợt cầu lông/pickleball, mua hàng online (phí phát sinh), đổi điểm thưởng, giả shop trả lời "chốt đơn", lừa
  "hoàn tiền" (QR/cổng hoàn tiền giả), khóa học trẻ em.
- **5 chủ đề chỉ có ở private:** lừa người bán (ảnh chuyển khoản giả, email "nhận tiền"), giả trường/BHXH thu tiền thẻ BHYT của con,
  dịch vụ hộ chiếu nhanh (đòi tài khoản VNeID), nạp game / mua bán tài khoản game (dụ trẻ lấy OTP của bố mẹ), chuyển đổi eSIM giả.
- **Tin hợp lệ chung**: tin gia đình, công việc, biến động số dư, cảnh báo của ngân hàng, người kể lại vụ suýt bị lừa.
- Tên cơ quan: tin **hợp lệ** dùng tên sau sắp xếp 2025 (bỏ cấp huyện từ 1/7/2025; "Chi cục Thuế khu vực" → "Thuế tỉnh/thành phố",
  "Đội Thuế cấp huyện" → "Thuế cơ sở"; Cục Hải quan; cấp/đổi GPLX do công an...). Tin lừa có thể dùng tên cũ — nhưng mẫu siêu khó dùng
  đúng tên mới để model không học tắt "tên cũ = lừa đảo".

## Chia tệp và chống rò rỉ

1. **Chia theo mẫu**: mỗi mẫu (một cách viết, có chỗ trống + `[[a|b]]`) chỉ thuộc một tệp, nên câu test không phải biến thể của câu train.
   Hội thoại ở train/public ghi "Người gọi/Người nghe" hoặc "Người nhắn/Tôi"; ở private ghi "A/B" hoặc "[giờ] tên:" (định dạng train không có).
2. **Lọc gần trùng** bằng cosine TF-IDF ký tự 3–5 (chữ thường, bỏ dấu, bỏ ký tự ẩn, đổi chữ Cyrillic về Latin, che link/số), so với
   27.994 tin đã có (data_v6, data_v7 train/val, mục B train, và dữ liệu của Trần — **chỉ dùng để đo độ giống, không chép câu nào**):
   - train: bỏ tin giống câu gốc 60 kiểu / test_suite ≥ 0,80 (1 tin), giống bất kỳ tin test nào ≥ 0,90 (0), giống 26 câu test theo
     difflib ≥ 0,50 (217 tin — các mẫu vô tình gần với 26 câu bị bỏ gần hết);
   - public mới: bỏ tin giống train/dữ liệu cũ ≥ 0,90 (0 tin);
   - private: bỏ tin giống dữ liệu cũ, train hoặc public ≥ 0,80 (3 tin). Sau lọc, độ giống lớn nhất của tin private với mọi thứ đã có là
     0,799 (trung vị 0,356; cột `giong_nhat_da_co`).
3. Trùng nguyên văn bị bỏ trên cả 3 tệp.

## Biến đổi chữ (cột `bien_doi`)

| Kiểu | Ví dụ | Có ở |
|---|---|---|
| `cach_chu` | "t à i  k h o ả n", "O.T.P", "ch0 c0c" | train, public, private |
| `ky_tu_an` | chèn ký tự rộng 0 (U+200B) giữa chữ | train, public, private |
| `so_bang_chu` | số tài khoản/điện thoại viết bằng chữ hoặc gạch nối (lọt qua bộ che số) | train, public, private |
| `tron_tieng_anh` | "chuyển khoản" → "transfer", "xác nhận" → "confirm" | train, public, private |
| `emoji` | 🔥 ⚠️ 👉... | train, public, private |
| `dong_hinh` | chữ Cyrillic giống Latin (а, о, е, с, р) trong từ khóa | **chỉ private** |
| `link_che` | "abc[.]top", "hxxps://", "(chấm)" — lọt qua bộ che link | **chỉ private** |
| `tien_to_dai` / `hau_to_dai` | thêm đoạn chào hỏi dài phía trước / lời dặn "không chia sẻ OTP" phía sau | **chỉ private** |

Xác suất đặt cho mỗi tin: train 25%, public 12%, private 55% (30% trong đó 2 kiểu); tin hợp lệ nửa mức đó và chỉ nhận kiểu "lành"
(emoji, trộn tiếng Anh; ở private thêm tiền tố/hậu tố). Tin đã biến đổi ít bị trùng hơn nên sau khi bỏ trùng tỉ lệ thực tế là: train 30%,
public 15% (trên tin mới), private 50%.

## Độ khó đo bằng các model Dyv có sẵn (`eval_v8.py` → `do_kho.md`, `do_kho.json`)

Các model **chưa thấy** câu nào của v8. Kết quả chỉ mô tả độ khó — **không** dùng để chọn hay bỏ tin. acc3 = đúng cả 3 mức (D-20);
acc30 = được cảnh báo đúng (lừa đảo/nghi ngờ ≥ 30%, hợp lệ < 30%).

| Model | Tệp | acc3 | acc30 | AUC lừa đảo/hợp lệ | Lừa đảo ≥ 30% | Lừa đảo ≥ 70% | Hợp lệ bị cảnh báo |
|---|---|---|---|---|---|---|---|
| Dyv6.0 | train | 72,0% | 83,4% | 0,932 | 86,9% | 75,5% | 16,8% |
| Dyv6.0 | public_test | 74,2% | 83,0% | 0,946 | 85,9% | 73,2% | 16,0% |
| Dyv6.0 | private_test | 69,6% | 78,9% | 0,894 | 74,3% | 55,2% | 11,3% |
| Dyv10.0 (bản đo) | train | 67,5% | 83,8% | 0,926 | 86,6% | 67,1% | 20,5% |
| Dyv10.0 (bản đo) | public_test | 74,1% | 84,6% | 0,934 | 86,2% | 70,7% | 14,3% |
| Dyv10.0 (bản đo) | private_test | **63,6%** | **76,1%** | **0,880** | **72,3%** | **46,6%** | 16,0% |
| Dyv11.0 | train | 68,7% | 85,5% | 0,948 | 90,1% | 70,9% | 16,7% |
| Dyv11.0 | public_test | 77,0% | 89,3% | 0,962 | 90,3% | 72,5% | 9,4% |
| Dyv11.0 | private_test | 66,9% | 80,3% | 0,910 | 76,6% | 50,4% | 12,6% |

- private khó hơn public với cả 3 model: acc3 thấp hơn 4,6–10,5 điểm, AUC thấp hơn khoảng 0,05; chỗ khó chính là tin lừa đảo — chỉ
  72–77% được cảnh báo (public 86–90%) và 47–55% bị kết luận lừa đảo (public 71–73%).
- Chủ đề chỉ có ở private: acc30 71–76%; chủ đề research ở private: 70–75% (ở public 98%).
- "Dyv10.0 (bản đo)" là bản train không gồm tập test, dùng cho mọi số đo trước đây (bản release trong `artifacts/Dyv10.0` học thêm cả
  `val_vi` và `test_vi_internal`). Phần V4C (bge-m3) và bản kết hợp **Dyv10.1** cần máy có mô hình V4C — **chưa đo**, xem T-42 trong `docs/TASKS.md`.

## Các cột

| Cột | Nghĩa |
|---|---|
| `id`, `template_id` | id tin; id mẫu (`V8_<chu_de>_<vai><nhãn><số>`; `GOC_SCAM_0xx` = câu gốc; `OLD_*` = tin test cũ) |
| `text` | tin đã che link/số điện thoại/dãy số dài như production (`[LINK]`, `[PHONE]`, `[NUMBER]`) — dùng cột này để đo |
| `text_raw` | tin trước khi che (số liệu giả) |
| `nhan`, `label`, `muc_tieu` | 3 mức; nhãn nhị phân (1/0, trống với nghi ngờ); xác suất mong muốn (1 / 0,5 / 0) |
| `ky_vong_ket_luan`, `ky_vong_rui_ro` | câu kết luận và dải % model nên đưa ra (D-20) |
| `muc_do`, `kenh`, `dang` | độ khó; kênh; `tin_nhan` / `hoi_thoai` / `cuoc_goi` |
| `chu_de`, `ten_chu_de`, `nhom_chu_de` | t01–t60, n_..., hop_le_chung, hoặc chủ đề của bộ test cũ |
| `kieu_lua`, `ten_kieu_lua`, `scenario` | kiểu cũ 1–29 (nếu khớp) và kịch bản trong `scenarios.yaml` (tin không lừa đảo: `KHONG_LUA_DAO`) |
| `nguon_chu_de` | `bo_60_kieu` · `research_v8` · `rieng_private` · `hop_le_chung` · `test_cu` |
| `chu_de_moi_voi_train`, `chi_co_o_private` | 1 nếu chủ đề không có trong train; 1 nếu chủ đề chỉ có ở private |
| `dau_hieu` | dấu hiệu chính / lý do của nhãn |
| `style`, `bien_doi` | kiểu viết (không dấu, teencode, gõ sai...); biến đổi chữ |
| `giong_nhat_da_co` | cosine lớn nhất với dữ liệu đã có (train: với các tệp test; public mới: với train + cũ; private: với mọi thứ) |
| `split`, `nguon` | tệp; nguồn (`mo_phong_v8` hoặc tệp test cũ) |

## Sinh lại và đo

```bash
cd ml/sms_dataset
python generate_dataset_v8.py --du-lieu-tran <thư mục data_processed/text của Trần>   # ~2 phút; thiếu templates_v8_rieng.py thì bỏ qua private
python eval_v8.py --dyv10-do <thư mục Dyv10.0 bản đo, train_dyv10.py không --release>  # -> data_v8/do_kho.md, do_kho.json
python eval_3muc.py --csv data_v8/sms_v8_public_test.csv --versions Dyv6.0 Dyv11.0      # bảng 3 mức theo kiểu cũ
```

Không có `--du-lieu-tran` thì vẫn chạy, nhưng chỉ lọc rò rỉ với dữ liệu trong kho (kết quả có thể khác một vài tin).

## Giới hạn

- Cùng một tác giả (AI) viết mẫu train và mẫu test: dù chia theo mẫu và lọc gần trùng, số đo vẫn lạc quan hơn tin thật.
- Mỗi mẫu cho nhiều tin chỉ khác chỗ trống và kiểu viết; số tin không bằng số "câu khác nhau" (train 285 mẫu, private 177 mẫu).
- Nhãn `nghi_ngo` ít ở private (43 tin) — ranh giới nghi ngờ/hợp lệ của tin thật cần người duyệt.
- Tên ngân hàng, sàn, nhà mạng, bệnh viện thật xuất hiện để mô phỏng tin giả mạo; không có nghĩa tổ chức đó liên quan.
- Bộ 60 kiểu chưa rõ nguồn gốc/giấy phép (QUESTION-58); hoangvt2501/data_scam chỉ là gợi ý khung kiểu lừa (qua danh sách 29 nhóm), không
  chép câu nào (QUESTION-41).

## Nguồn tham khảo thủ đoạn (chỉ đọc để lấy ý, không chép câu chữ)

- Bắt cóc online: [Nhân Dân — Ngăn chặn tội phạm "bắt cóc online"](https://nhandan.vn/ngan-chan-toi-pham-bat-coc-online-post952500.html), [Tuổi Trẻ — Cách nào ngăn "bắt cóc online" học sinh, sinh viên?](https://tuoitre.vn/cach-nao-ngan-bat-coc-online-hoc-sinh-sinh-vien-20250810234540125.htm), [Nhân Dân — Phòng ngừa thủ đoạn bắt cóc, tống tiền trên mạng](https://nhandan.vn/ocop/phong-ngua-thu-doan-bat-coc-tong-tien-tren-mang-post899317.html)
- Đổi tiền mới: [hatinh.gov.vn — Cẩn trọng sập bẫy lừa đổi tiền mới, tiền lẻ giá rẻ](https://hatinh.gov.vn/vi/bai-viet/can-trong-sap-bay-lua-doi-tien-moi-tien-le-gia-re), [hatinh.gov.vn — Đổi tiền lẻ, tiền mới để thu lời là hành vi trái pháp luật](https://hatinh.gov.vn/vi/bai-viet/doi-tien-le-tien-moi-de-thu-loi-la-hanh-vi-trai-phap-luat), [PLO — Cẩn trọng với dịch vụ đổi tiền mới dịp Tết](https://plo.vn/can-trong-voi-dich-vu-doi-tien-moi-dip-tet-post772593.html)
- Ngoại tệ: [VOH — Bắt đối tượng lừa đảo "đổi tiền ngoại tệ online"](https://voh.com.vn/phap-luat/bat-doi-tuong-lua-dao-doi-tien-ngoai-te-online-chiem-doat-66000-usd-615191.html), [Thị trường Tài chính Tiền tệ — Thủ đoạn lừa đảo thông qua đổi tiền ngoại tệ online](https://thitruongtaichinhtiente.vn/thu-doan-lua-dao-thong-qua-doi-tien-ngoai-te-online-70268.html), [Đại Đoàn Kết — mạo danh người thân lừa đổi tiền](https://daidoanket.vn/bat-doi-tuong-chuyen-mao-danh-nguoi-than-lua-doi-tien-chiem-doat-tien-ty-10308192.html), [VOV — lừa chuyển tiền Việt Nam – Hàn Quốc](https://vov.vn/phap-luat/bat-nhom-lua-dao-chuyen-tien-viet-nam-han-quoc-chiem-doat-so-tien-rat-lon-post1312420.vov)
- Vàng: [Nhân Dân — Mua bán vàng bạc online và những chiêu trò lừa đảo](https://nhandan.vn/mua-ban-vang-bac-online-va-nhung-chieu-tro-lua-dao-post919074.html), [Nhân Dân — Cảnh giác bẫy lừa mua bán vàng trên mạng](https://nhandan.vn/canh-giac-bay-lua-mua-ban-vang-tren-mang-post927007.html), [Thị trường Tài chính Tiền tệ — "bẫy" đầu tư, mua vàng online](https://thitruongtaichinhtiente.vn/canh-giac-voi-cac-bay-lua-dao-dau-tu-mua-vang-online-83167.html)
- Vợt pickleball, trao đổi đồ: [Báo Lào Cai — lừa đảo trao đổi vợt Pickleball](https://baolaocai.vn/canh-bao-thu-doan-lua-dao-trao-doi-vot-pickleball-tren-mang-xa-hoi-post393718.html), [Đại Đoàn Kết — chốt đơn mua vợt pickleball cũ](https://daidoanket.vn/can-trong-khi-chot-don-mua-vot-pickleball-cu-tren-mang-xa-hoi-10296097.html), [VOH — giả "Liên đoàn Pickleball Việt Nam"](https://voh.com.vn/phap-luat/bo-cong-an-canh-bao-thu-doan-lua-dao-lien-doan-pickleball-viet-namchiem-doat-tien-ti-568279.html)
- Mua hàng, chốt đơn: [hatinh.gov.vn — mua hàng thanh lý qua mạng](https://hatinh.gov.vn/vi/bai-viet/canh-giac-sap-bay-lua-dao-khi-mua-hang-thanh-ly-qua-mang), [hatinh.gov.vn — chốt đơn mua hàng công khai trên mạng xã hội](https://hatinh.gov.vn/vi/page/du-lich/bai-viet/can-than-sap-bay-lua-dao-khi-chot-don-mua-hang-cong-khai-tren-mang-xa-hoi)
- Điểm thưởng: [VPBank — Cảnh giác chiêu thức lừa đổi điểm thưởng nhận quà](https://www.vpbank.com.vn/bi-kip-va-chia-se/retail-story-and-tips/goc-canh-giac/canh-giac-chieu-thuc-lua-doi-diem-thuong-nhan-qua)
- Hoàn tiền, shipper: [Nhân Dân — giả mạo hoàn tiền và đơn hàng](https://nhandan.vn/ocop/canh-giac-chieu-tro-gia-mao-hoan-tien-va-don-hang-post955578.html), [LSVN — giả danh shipper lừa "hoàn tiền"](https://lsvn.vn/canh-bao-thu-doan-gia-danh-shipper-don-vi-giao-hang-lua-dao-chiem-doat-tai-san-a177201.html)
- Thẻ BHYT của con, giả giáo viên/nhân viên y tế: [Nhân Dân — Chiêu lừa "thẻ bảo hiểm của con"](https://nhandan.vn/ocop/video-chieu-lua-the-bao-hiem-cua-con-nham-vao-cac-me-sau-sinh-post989446.html), [Báo Lào Cai — thủ đoạn "tích hợp BHYT" cho con](https://baolaocai.vn/cuc-an-ninh-mang-canh-bao-canh-giac-thu-doan-tich-hop-bhyt-cho-con-post911470.html), [Nhân Dân — Giả danh giáo viên, nhân viên y tế](https://special.nhandan.vn/gia-danh-nhan-vien-y-te-bao-nguoi-than-cap-cuu/index.html)
- SIM/eSIM: [Techcombank — lừa đảo nâng cấp SIM](https://techcombank.com/thong-tin/thong-bao/khuyen-cao-chieu-tro-lua-dao-nang-cap-sim-dien-thoai-de-chiem-doat-tien-trong-tai-khoan-ngan-hang), [VNBA — BacABank cảnh báo lừa đảo qua SIM](https://vnba.org.vn/vi/bacabank-canh-bao-chieu-thuc-lua-dao-qua-sim-dien-thoai--so-dien-thoai-4747.htm)
- Sắp xếp bộ máy 2025: [VOH — Chính thức bỏ cấp huyện từ 1/7](https://voh.com.vn/xa-hoi/chinh-thuc-bo-cap-huyen-tu-17-599990.html), [VCCI — đồng bộ tên gọi trong hệ thống thuế](https://vcci.com.vn/tin-tuc/dong-bo-ten-goi-chuc-danh-va-tham-quyen-trong-he-thong-thue)
