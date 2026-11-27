# Nguồn tin SMS thật

Các file trong thư mục này (`train_vi_only.csv`, `val_vi.csv`, `test_vi_internal.csv`; 2.547 tin) lấy từ:

**Vietnamese Quality-Assured SMS Scam Dataset** — Tran Nguyen Thai Tuan, Le Hoang Khang, Nguyen Minh Tai, Nguyen Van Thang,
Mai Hoang Dinh (2026). https://github.com/trannguyenthaituan251209/vietnamese_sms_dataset — giấy phép
**Creative Commons Attribution 4.0 International (CC BY 4.0)**, https://creativecommons.org/licenses/by/4.0/.
Bài báo đi kèm (theo README của bộ dữ liệu): "Vietnamese SMS Dataset with Quality Assurance", IEEE Access, 2026.

Đội đã sửa đổi: thành viên Trần bỏ 444 tin trùng, sửa nhẹ khoảng 40 tin, chia lại thành train 1.911 / val 382 / test 254
(kho 12do/Datasets-for-ScamRadar-Risk-Model, commit `7420da5`). Đối chiếu 27/11/2026: 2.507/2.547 tin trùng nguyên văn bản gốc.
Thông tin cá nhân đã được tác giả thay bằng token (`[PHONE]`, `[BANK_ACC]`, `[MONEY]`, `[NUMBER]`, `[TIME]`, `[DATE]`).
