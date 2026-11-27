"""Đặc trưng "dấu hiệu nguy hiểm" (red flags) đọc được bằng mắt, tính trên văn bản đã chuẩn hoá (chữ thường, BỎ DẤU,
[LINK]/[PHONE]/[NUMBER] -> xxlink/xxphone/xxnumber).

Mỗi đặc trưng là một HÀNH VI mà tin lừa đảo hay có (đòi chuyển tiền, đòi mã, dọa, giữ bí mật...), không phụ thuộc chủ đề.
TF-IDF học được TỪ; các cờ này giúp model nhận ra cùng một hành vi dù câu chữ mới. Danh sách là đề xuất, sửa thoải mái.
"""

from __future__ import annotations

import re

import numpy as np

_W = r"[\w/]*"  # đuôi từ (cho phép viết tắt)

FLAGS: dict[str, str] = {
    # đòi chuyển / nộp tiền vào một tài khoản
    "doi_chuyen_tien": r"\b(chuyen|ck|nop|dong|gui|nap|thanh toan|hoan|tra lai|ung)\b.{0,45}\b(xxnumber|stk|tai khoan|tk|so tai khoan|usdt|vi)\b",
    # tài khoản lạ: cá nhân / tạm giữ / an toàn / số khác / số mới
    "tai_khoan_la": r"tai khoan (tam giu|an toan|ca nhan|bao lanh|khac|moi)|stk (ca nhan|khac|moi)|so (tai khoan )?moi|doi (so )?tai khoan|tai khoan .{0,15}chi dinh",
    # đòi mã: đọc / gửi / nhập / cung cấp OTP, mã xác nhận, dãy số
    "doi_ma": r"\b(doc|cung cap|gui|nhap|dien|bao|cho)\b.{0,30}\b(otp|ma xac|ma so|day so|ma kich hoat|mat khau)",
    # câu PHỦ ĐỊNH về mã (tin OTP thật): "không chia sẻ / không cung cấp mã"
    "phu_dinh_ma": r"\b(khong|ko|k|hong|dung|tuyet doi khong|khong bao gio)\b.{0,25}\b(chia se|cung cap|doc|hoi|yeu cau)\b.{0,30}\b(otp|ma)",
    "co_link": r"xxlink",
    "co_sdt": r"xxphone",
    "co_so_dai": r"xxnumber",
    "gap": r"\b(gap|khan|ngay lap tuc|ngay hom nay|het han|qua han|trong \d+ ?(gio|h|phut)|truoc \d+h|con \d+ (gio|phut))\b",
    "doa": r"\b(khoa|phong toa|cuong che|truy na|lenh bat|bat giu|khoi kien|tung|cat dien|ngung cap|niem phong|bao cong an|dung trach|gui cho nguoi than)\b",
    "giu_bi_mat": r"giu bi mat|khong (duoc )?noi|dung goi|khong tiet lo|khong chia se cuoc|dung bao|khong can bao|khong den truc tiep",
    "phi_truoc": r"\bphi\b|le phi|tien coc|dat coc|\bcoc\b|kich hoat|mo khoa",
    "qua_thuong": r"trung thuong|trung giai|qua tang|nhan qua|tri an|may man|chuc mung|nhan thuong|quay vao o",
    "cai_ung_dung": r"\b(cai|tai)\b.{0,15}\b(app|ung dung)\b|cap quyen|tro nang",
    "co_quan": r"cong an|vien kiem sat|toa an|co quan dieu tra|bao hiem xa hoi|\bbhxh\b|cuc thue|chi cuc thue|\bcsgt\b|dich vu cong|vneid",
    "canh_bao": r"canh giac|canh bao|luu y|khuyen cao|de phong|phong tranh|nhac\b",
    "menh_lenh": r"\b(vui long|hay|de nghi|yeu cau|quy khach can|ban can|bam vao|truy cap|lien he ngay)\b",
    "loi_nhuan": r"loi nhuan|lai \d+|cam ket|hoa hong|x\d+ tai khoan|nhan doi|thang lon|lenh",
    "nguoi_quen_doi_so": r"(doi|mat|hong|muon) (so|sim|may|dien thoai|zalo)|so moi|zalo moi|dang hop|ket o",
    "tien_lon": r"\b\d{2,3}[.,]?\d{0,3}[.,]?\d{0,3} ?(trieu|tr|cu)\b|\d{2,3}\.\d{3}\.\d{3}|xxtien_lon",
}
FLAG_NAMES = list(FLAGS)
_COMPILED = [re.compile(p) for p in FLAGS.values()]


def flag_matrix(texts_norm: list[str]) -> np.ndarray:
    """Ma trận 0/1 (n x số cờ) + 2 cờ kết hợp."""
    base = np.array([[1.0 if rx.search(t) else 0.0 for rx in _COMPILED] for t in texts_norm])
    i = {n: k for k, n in enumerate(FLAG_NAMES)}
    # giả vờ cảnh báo: có lời cảnh báo NHƯNG lại đòi tiền / đòi mã / đưa link
    # (trừ khi câu có lời dặn KHÔNG chia sẻ mã: tin cảnh báo thật hay nhắc "ai đòi đọc mã thì gác máy").
    gia_vo = (base[:, i["canh_bao"]] * (1 - base[:, i["phu_dinh_ma"]])
              * np.maximum.reduce([base[:, i["doi_chuyen_tien"]], base[:, i["doi_ma"]], base[:, i["co_link"]]]))
    # OTP thật: phủ định về mã mà không đòi tiền, không link
    otp_that = base[:, i["phu_dinh_ma"]] * (1 - base[:, i["doi_chuyen_tien"]]) * (1 - base[:, i["co_link"]])
    return np.hstack([base, gia_vo[:, None], otp_that[:, None]])


ALL_FLAG_NAMES = FLAG_NAMES + ["gia_vo_canh_bao", "otp_that"]


def explain(texts_norm: list[str]) -> list[list[str]]:
    m = flag_matrix(texts_norm)
    return [[ALL_FLAG_NAMES[j] for j in np.nonzero(row)[0]] for row in m]

# Tên hiển thị tiếng Việt
FLAG_LABELS = {
    "doi_chuyen_tien": "đòi chuyển tiền", "tai_khoan_la": "tài khoản lạ/tạm giữ", "doi_ma": "đòi mã OTP/mật khẩu",
    "phu_dinh_ma": "dặn không chia sẻ mã", "co_link": "có link", "co_sdt": "có SĐT", "co_so_dai": "có STK/số dài",
    "gap": "hối thúc", "doa": "đe dọa", "giu_bi_mat": "bắt giữ bí mật", "phi_truoc": "đòi phí/cọc trước",
    "qua_thuong": "trúng thưởng/quà", "cai_ung_dung": "bắt cài ứng dụng", "co_quan": "nhắc cơ quan nhà nước",
    "canh_bao": "lời cảnh báo", "menh_lenh": "ra lệnh", "loi_nhuan": "hứa lợi nhuận/hoa hồng",
    "nguoi_quen_doi_so": "người quen đổi số/mượn máy", "tien_lon": "số tiền lớn",
    "gia_vo_canh_bao": "giả vờ cảnh báo", "otp_that": "giống tin OTP thật",
    # Dyv6.0
    "co_stk": "có số tài khoản", "nhan_qc": "có nhãn quảng cáo [QC]", "tu_choi_qc": "có cách từ chối quảng cáo",
    "cu_phap_dau_so": "cú pháp soạn tin gửi đầu số", "thong_bao_giao_dich": "dạng thông báo giao dịch/số dư",
    "kenh_chinh_thuc": "chỉ về kênh chính thức (ứng dụng, quầy, tổng đài)", "lien_he_ngoai_kenh": "kéo sang Zalo/Telegram",
    "link_xac_thuc": "link kèm yêu cầu đăng nhập/xác thực/nhập thông tin", "link_de_doa": "link kèm đe dọa khóa/phạt",
    "phi_de_nhan": "đòi phí để được nhận tiền/quà/hàng", "thuong_hieu_so_ca_nhan": "xưng ngân hàng/nhà mạng/cơ quan nhưng đưa SĐT cá nhân",
}


# ---------------------------------------------------------------------------
# Dyv6.0 — bộ cờ mới, tính trên văn bản chuẩn hoá bằng vn_text.normalize_vi6 (số -> xxso, tiền -> xxtien, giờ -> xxgio,
# ngày -> xxngay, mã chữ+số -> xxma, nhãn quảng cáo -> xxqc). Bộ cờ cũ (FLAGS ở trên) GIỮ NGUYÊN cho Dyv2.0–5.0.
#
# Sửa các cờ hay báo nhầm trên tin thật (đo 25/11):
#   - "có STK/số dài" bật với MỌI [NUMBER] -> nay "co_stk" chỉ bật khi con số đi với "STK / tài khoản / tên ngân hàng".
#   - "đòi chuyển tiền" khớp "gửi [NUMBER]" (soạn tin gửi đầu số) -> nay cần "vào <số>" hoặc chữ "tài khoản".
#   - "đòi phí" khớp cả "MIỄN PHÍ" -> nay chỉ khi có động từ nộp/đóng/chuyển phí hoặc "phí ... trước / để nhận".
#   - "lời cảnh báo" khớp "đêm nhạc" (nhac) -> nay chỉ "nhắc nhở/nhắc lại...".
# Thêm DẤU HIỆU TIN HỢP LỆ (model tự học trọng số, có thể âm): nhãn [QC], cách từ chối quảng cáo, cú pháp soạn tin gửi đầu số,
# dạng thông báo giao dịch/số dư, chỉ về kênh chính thức. Và vài cờ kết hợp của tin lừa đảo (link + đòi đăng nhập/xác thực,
# link + đe dọa, phí để được nhận, xưng thương hiệu nhưng đưa SĐT cá nhân, kéo sang Zalo/Telegram).
# ---------------------------------------------------------------------------
_BANK_WORDS = (r"vietcombank|techcombank|vietinbank|bidv|agribank|\bacb\b|sacombank|vpbank|tpbank|mb ?bank|hdbank|\bocb\b|"
               r"\bshb\b|seabank|\bvib\b|\bmsb\b|\bvcb\b|\btcb\b|\bctg\b|\bagr\b|\bstb\b|\bvpb\b|\btpb\b")
FLAGS_V6: dict[str, str] = {
    "doi_chuyen_tien": r"\b(chuyen|chuyen khoan|nop|dong|nap|thanh toan|hoan|tra lai|ung|gui)\b.{0,40}\b(so tai khoan|tai khoan|vi|usdt)\b"
                       r"|\b(chuyen|chuyen khoan|nop|dong|nap)\b.{0,30}\bvao\b.{0,6}xxso",
    "tai_khoan_la": r"tai khoan (tam giu|an toan|ca nhan|bao lanh|khac|moi)|so tai khoan (ca nhan|khac|moi)|so (tai khoan )?moi|"
                    r"doi (so )?tai khoan|tai khoan .{0,15}chi dinh|tai khoan (cua )?(nhan vien|ban con|ban em|nguoi khac)|"
                    r"so tai khoan (cua )?(ban|nhan vien)",
    "co_stk": r"\b(so tai khoan|tai khoan)\b\W{0,3}(so\W{0,2})?xxso|xxso\W{0,3}(" + _BANK_WORDS + r")",
    "doi_ma": r"\b(doc|cung cap|gui|nhap|dien|bao|cho|tra loi)\b.{0,30}\b(otp|ma xac|ma so|day so|ma kich hoat|mat khau|so the)",
    "phu_dinh_ma": FLAGS["phu_dinh_ma"],
    "co_link": r"xxlink",
    "co_sdt": r"xxphone",
    "gap": r"\b(gap|khan|khan cap|ngay lap tuc|ngay hom nay|trong ngay|het han|qua han|trong xxgio|trong xxso ?(gio|tieng|phut)|"
           r"truoc xxgio|sau xxgio|sau xxso ?(gio|tieng|ngay)|con xxso (gio|phut))\b",
    "doa": r"\b(khoa|phong toa|cuong che|truy na|lenh bat|bat giu|khoi kien|tung|cat dien|ngung cap|niem phong|bao cong an|"
           r"dung trach|gui cho nguoi than|vinh vien|thu hoi|vo hieu|dinh chi|tam giu|tieu huy|xet xu vang mat|tang them|bi phat|ngat)\b",
    "giu_bi_mat": FLAGS["giu_bi_mat"],
    "phi_truoc": r"\b(dong|nop|chuyen|tra)\b.{0,20}\b(phi|le phi)\b|\bphi\b.{0,25}\b(truoc|de (nhan|giai ngan|mo|kich hoat|giu))\b|"
                 r"tien coc|dat coc|\bcoc\b",
    "qua_thuong": FLAGS["qua_thuong"],
    "cai_ung_dung": FLAGS["cai_ung_dung"] + r"|\bapk\b|ho tro tu xa",
    "co_quan": FLAGS["co_quan"],
    "canh_bao": r"canh giac|canh bao|luu y|khuyen cao|de phong|phong tranh|\bnhac (nho|lai|moi nguoi|ca nha|ba me|quy khach|khach hang)\b",
    "menh_lenh": FLAGS["menh_lenh"],
    "loi_nhuan": r"loi nhuan|lai xxso|cam ket|hoa hong|xxma tai khoan|nhan doi|thang lon|\blenh\b",
    "nguoi_quen_doi_so": FLAGS["nguoi_quen_doi_so"],
    # dấu hiệu tin hợp lệ của thương hiệu (trọng số do model học)
    "nhan_qc": r"\bxxqc\b",
    "tu_choi_qc": r"tu choi (nhan )?(qc|quang cao|tin)|huy (nhan )?(qc|quang cao)|soan (tc|huy qc)\b|\bdnc\b",
    "cu_phap_dau_so": r"\bsoan\b.{1,30}\bgui (xxso|xxma)\b",
    "thong_bao_giao_dich": r"\b(sd|so du)\b\W{0,3}(kha dung\W{0,3})?(xxtien|xxso)|[+-] ?xxtien|\bnd\b ?:|\bref\b|ma giao dich|"
                           r"da (thanh toan|nhan|nap|thuc hien) thanh cong",
    "kenh_chinh_thuc": r"\b(tren|qua|trong) (ung dung|app)\b|tai (cua hang|quay|diem giao dich|chi nhanh|buu cuc|tram y te|ubnd|uy ban|"
                       r"tru so|van phong|dai ly)|(tong dai|hotline|lien he|goi)\W{0,3}xxso\b|in (o )?(mat )?sau the|chinh thuc",
    # dấu hiệu lừa đảo
    # chỉ khi MỜI liên hệ / kết bạn / vào nhóm qua Zalo, Telegram... (tin OTP thật của Zalo không bật cờ này)
    "lien_he_ngoai_kenh": r"\b(ket ban|lien he|nhan tin|nhan|inbox|tham gia|vao nhom|add)\b\W{0,12}(qua |voi )?(zalo|telegram|tele|whatsapp|viber)\b|"
                          r"\b(zalo|telegram|whatsapp|viber)\W{0,3}(xxphone|xxso)\b|nhom kin|nhom (zalo|telegram)|"
                          r"\b(lam viec|nhan viec|huong dan|lam ho so|ho tro) (qua|tren) (zalo|telegram|whatsapp|viber)\b",
}
FLAG_NAMES_V6 = list(FLAGS_V6)
_COMPILED_V6 = [re.compile(p) for p in FLAGS_V6.values()]
_LINK_ACTION = re.compile(r"dang nhap|xac thuc|xac minh|cap nhat|kich hoat|mo khoa|\bnhap\b|dien thong tin|khai bao|xac nhan|"
                          r"doi diem|nhan qua|nhan thuong|nhan giai|nhan tien|huy giao dich|nop phat|thanh toan|nap tien|quay ngay")
_RECEIVE = re.compile(r"nhan (qua|thuong|giai|tien|hang|ve|luong)|giai ngan|rut (tien|thuong)|de nhan|hoan tien|giu (cho|phong|suat|xe)")
_BRAND_OFFICIAL = re.compile(_BANK_WORDS + r"|momo|zalopay|viettel|vinaphone|mobifone|vnpt|\bevn|dien luc|bhxh|bao hiem xa hoi|"
                             r"cong an|vien kiem sat|toa an|co quan thue|cuc thue|vneid|ngan hang")


def flag_matrix_v6(texts_norm: list[str]) -> np.ndarray:
    """Ma trận 0/1 (n x 30): 24 cờ cơ bản + 6 cờ kết hợp."""
    base = np.array([[1.0 if rx.search(t) else 0.0 for rx in _COMPILED_V6] for t in texts_norm])
    i = {n: k for k, n in enumerate(FLAG_NAMES_V6)}
    gia_vo = (base[:, i["canh_bao"]] * (1 - base[:, i["phu_dinh_ma"]])
              * np.maximum.reduce([base[:, i["doi_chuyen_tien"]], base[:, i["doi_ma"]], base[:, i["co_link"]]]))
    otp_that = base[:, i["phu_dinh_ma"]] * (1 - base[:, i["doi_chuyen_tien"]]) * (1 - base[:, i["co_link"]])
    act = np.array([1.0 if _LINK_ACTION.search(t) else 0.0 for t in texts_norm])
    recv = np.array([1.0 if _RECEIVE.search(t) else 0.0 for t in texts_norm])
    brand = np.array([1.0 if _BRAND_OFFICIAL.search(t) else 0.0 for t in texts_norm])
    link_xac_thuc = base[:, i["co_link"]] * act
    link_de_doa = base[:, i["co_link"]] * base[:, i["doa"]]
    phi_de_nhan = base[:, i["phi_truoc"]] * recv
    thuong_hieu_sdt = brand * base[:, i["co_sdt"]]
    combos = np.stack([gia_vo, otp_that, link_xac_thuc, link_de_doa, phi_de_nhan, thuong_hieu_sdt], axis=1)
    return np.hstack([base, combos])


ALL_FLAG_NAMES_V6 = FLAG_NAMES_V6 + ["gia_vo_canh_bao", "otp_that", "link_xac_thuc", "link_de_doa", "phi_de_nhan",
                                     "thuong_hieu_so_ca_nhan"]

# Bộ cờ theo phiên bản: model cũ (không có thuộc tính flag_set) dùng "v5".
FLAG_SETS = {"v5": (flag_matrix, ALL_FLAG_NAMES), "v6": (flag_matrix_v6, ALL_FLAG_NAMES_V6)}


def flag_set_of(model):
    """(hàm tính cờ, danh sách tên cờ) đúng với model (ScamRiskModel hoặc ScamRouter)."""
    base = getattr(model, "base", model)
    return FLAG_SETS[getattr(base, "flag_set", "v5")]
