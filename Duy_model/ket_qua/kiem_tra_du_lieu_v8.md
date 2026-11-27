# Kiểm tra chất lượng bộ v8 (train / public_test / private_test)

Tạo bằng `python kiem_tra_du_lieu.py`. Chỉ đếm, không in nội dung tin.

## 1. Cấu trúc và phân bố

| Tệp | Số tin | Thiếu cột | Tin trống | Nhãn lạ | Lừa đảo / nghi ngờ / hợp lệ | Độ khó | Dạng tin |
|---|---|---|---|---|---|---|---|
| train | 5886 | không | 0 | 0 | 2936 / 902 / 2048 | de 1180, kho 1428, sieu_kho 480, trung_binh 2798 | cuoc_goi 96, hoi_thoai 368, tin_nhan 5422 |
| public_test | 2179 | không | 0 | 0 | 1017 / 183 / 979 | de 85, kho 643, khong_ro 122, sieu_kho 13, trung_binh 1316 | cuoc_goi 70, hoi_thoai 16, tin_nhan 2093 |
| private_test | 828 | không | 0 | 0 | 397 / 43 / 388 | kho 58, sieu_kho 770 | hoi_thoai 81, tin_nhan 747 |

## 2. Trùng lặp và rò rỉ giữa các tệp

| Kiểm | train | public_test | private_test |
|---|---|---|---|
| Mã tin trùng trong tệp | 0 | 0 | 0 |
| Câu trùng nguyên văn trong tệp | 0 | 7 | 0 |

| Cặp tệp | Mã tin chung | Câu chung (nguyên văn) | Mẫu câu (template) chung | Câu test gần giống câu train (cosine ≥ 0,9) |
|---|---|---|---|---|
| train ↔ public_test | 0 | 0 | 0 | 0 |
| train ↔ private_test | 0 | 0 | 0 | 0 |
| public_test ↔ private_test | 0 | 0 | 0 | 0 |

## 3. Dữ liệu cá nhân (Điều 12.4 thể lệ)

| Tệp | Số điện thoại | Ngoài dải giả `09xx 000 xxx` | Email | Dãy 9–16 chữ số |
|---|---|---|---|---|
| train | 240 | 0 | 3 (tên miền: l0pay-dinhdanh.club, l0pay.net, l0payuudai.site) | 661 |
| public_test | 85 | 0 | 1 (tên miền: abc.vn) | 294 |
| private_test | 8 | 0 | 0 (tên miền: –) | 31 |

## Kết luận

**Không phát hiện lỗi.**
