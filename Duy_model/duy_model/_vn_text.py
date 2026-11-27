"""Dyv5.0 — chuẩn hoá tin nhắn tiếng Việt KHÔNG DẤU / VIẾT TẮT trước khi mã hoá.

Tin SMS/Zalo thật hay gõ không dấu và viết tắt: "a oi e dag hop ko nghe dc, a ck gium e 3 cu vo tk ban e".
Mô hình chỉ học được từ những gì nó nhìn thấy, nên ta đưa mọi cách viết về MỘT dạng chuẩn (không dấu) trước:

  1. chữ thường + bỏ dấu ("trúng thưởng" -> "trung thuong")           [đã có từ Dyv1.0]
  2. gộp ký tự kéo dài ("gapppp" -> "gap", "oiiii" -> "oi")
  3. SỐ TIỀN -> nhãn theo độ lớn: "500k" -> xxtien_nho, "5 trieu"/"5tr"/"5 cu" -> xxtien_vua, "30 trieu" -> xxtien_lon
     (mô hình học "đòi số tiền lớn" thay vì học thuộc con số "500k")
  4. viết tắt / teencode -> từ đầy đủ ("ko" -> "khong", "ck" -> "chuyen khoan", "stk" -> "so tai khoan", "dc" -> "duoc"...)

Từ điển viết tắt lấy theo cách viết phổ biến trên SMS/mạng xã hội; KHÔNG đưa vào những từ mơ hồ khi bỏ dấu
(ví dụ "vo" = vào/vợ, "c" = chị/có, "mk" = mình/mật khẩu, "dg" = đang/đăng) để không làm sai nghĩa.
Sửa/thêm từ: sửa ABBREVIATIONS bên dưới rồi train lại.
"""

from __future__ import annotations

import re
import unicodedata

ABBREVIATIONS: dict[str, str] = {
    # phủ định / khẳng định
    "ko": "khong", "k": "khong", "kh": "khong", "khg": "khong", "kg": "khong", "hong": "khong", "hok": "khong",
    "hk": "khong", "khum": "khong", "k0": "khong", "dc": "duoc", "dk": "dang ky", "dky": "dang ky",
    # chuyển tiền / tài khoản
    "ck": "chuyen khoan", "stk": "so tai khoan", "tk": "tai khoan", "sdt": "so dien thoai", "dt": "dien thoai",
    "dthoai": "dien thoai", "nh": "ngan hang",
    # đại từ, xưng hô
    "e": "em", "a": "anh", "b": "ban", "bn": "ban", "mik": "minh", "mjk": "minh", "mn": "moi nguoi", "mng": "moi nguoi",
    "ng": "nguoi", "t": "toi",
    # từ hay gặp
    "gium": "giup", "dum": "giup", "jup": "giup", "dag": "dang", "j": "gi", "ji": "gi", "r": "roi", "vs": "voi",
    "lm": "lam", "bt": "biet", "bik": "biet", "hnay": "hom nay", "hqua": "hom qua", "nv": "nhan vien",
    "sp": "san pham", "tb": "thong bao", "ttin": "thong tin", "ctv": "cong tac vien", "ib": "inbox",
    "zl": "zalo", "fb": "facebook", "lh": "lien he", "nhaa": "nha", "nhee": "nhe", "trc": "truoc", "ntn": "nhu the nao",
    "cty": "cong ty", "ad": "admin", "kq": "ket qua", "dthu": "doanh thu", "vn": "viet nam",
}
# "kh" vừa là "không" vừa là "khách hàng"; trong tin nhắn đòi tiền/đặt hàng thường là "khách hàng" khi đứng trước "than thiet/hang"
_KH_CUSTOMER = re.compile(r"\bkh (?=than thiet|hang\b|vip\b|moi\b)")

_UNITS = {"k": 1e3, "nghin": 1e3, "ngan": 1e3, "tr": 1e6, "trieu": 1e6, "cu": 1e6, "ty": 1e9, "ti": 1e9,
          "d": 1, "dong": 1, "vnd": 1, "usd": 25e3, "usdt": 25e3}
_MONEY = re.compile(r"(?<![\w.])(\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)\s?(k|nghin|ngan|tr|trieu|cu|ty|ti|vnd|dong|d|usdt|usd)\b")
_REPEAT = re.compile(r"([a-z])\1{2,}")
_ABBR = re.compile(r"\b(" + "|".join(sorted(map(re.escape, ABBREVIATIONS), key=len, reverse=True)) + r")\b")


def strip_diacritics(text: str) -> str:
    t = text.replace("đ", "d").replace("Đ", "D")
    return "".join(ch for ch in unicodedata.normalize("NFKD", t) if not unicodedata.combining(ch))


def _money_token(m: re.Match) -> str:
    raw, unit = m.group(1), m.group(2)
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", raw):
        value = float(re.sub(r"[.,]", "", raw))
    else:
        value = float(raw.replace(",", "."))
    value *= _UNITS[unit]
    if value < 1e6:
        return " xxtien_nho "
    if value < 1e7:
        return " xxtien_vua "
    return " xxtien_lon "


def normalize_vi(text: str) -> str:
    """Văn bản (đã che SĐT/STK/link) -> dạng chuẩn không dấu dùng cho TF-IDF, cờ dấu hiệu và vector."""
    t = strip_diacritics(text).lower()
    t = t.replace("[link]", " xxlink ").replace("[phone]", " xxphone ").replace("[number]", " xxnumber ")
    t = _REPEAT.sub(r"\1", t)
    t = _MONEY.sub(_money_token, t)
    t = _KH_CUSTOMER.sub("khach hang ", t)
    t = _ABBR.sub(lambda m: ABBREVIATIONS[m.group(1)], t)
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------------------
# Dyv6.0 — đưa MỌI cách che số về cùng một dạng.
#
# Production che: link -> [LINK], SĐT -> [PHONE], dãy >= 7 chữ số -> [NUMBER], số ngắn giữ nguyên.
# Bộ dữ liệu khác của đội che MỌI con số: [MONEY], [DATE], [TIME], [NUMBER] (cả năm, mã dịch vụ, đầu số ngắn).
# Đo 25/11: chỉ riêng khác biệt này đã làm cờ "có STK/số dài" bật ở 82% tin hợp lệ bị báo nhầm. Dyv6.0 đưa cả hai về:
#   tiền -> xxtien · ngày -> xxngay · giờ -> xxgio · mọi con số khác (kể cả [NUMBER], đầu số, OTP) -> xxso
#   link -> xxlink · SĐT -> xxphone · nhãn quảng cáo [QC]/(QC)/QC:/[AD] đầu tin -> xxqc
# Bỏ phân biệt tiền nhỏ/vừa/lớn của Dyv5.0 (bản che [MONEY] không cho biết độ lớn, giữ lại thì hai kiểu che lệch nhau).
# ---------------------------------------------------------------------------
_V6_MONEY = re.compile(r"(?<![\w.,])(\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)\s?(k|nghin|ngan|tr|trieu|cu|ty|ti|vnd|dong|d|usdt|usd)(?!\w)")
_V6_DATE = re.compile(r"(?<![\d/])\d{1,2}/\d{1,2}(?:/\d{2,4})?(?![\d/])")
_V6_TIME = re.compile(r"(?<![\w:])\d{1,2}(?::\d{2}(?::\d{2})?|h\d{2}|h|g\d{2})(?![\w:])")
_V6_CODE = re.compile(r"\b(?=[a-z]*\d)(?=\d*[a-z])[a-z0-9]{2,}\b")   # mã lẫn chữ và số: V120, PE0123..., 51F, FT2633..., 4GB
_V6_DIGITS = re.compile(r"\d+(?:[.,]\d+)*")
_V6_QC_HEAD = re.compile(r"^\s*(?:[\[(]\s*(?:qc|ad)\s*[\])]\s*[:\-]?|qc\s*[:\-]|qc(?=\s))")
_NUM_STANDIN = "9999999"  # [NUMBER] tạm thành một dãy số để "PE[NUMBER]" và "PE0123..." ra cùng một dạng
_V6_PLACEHOLDERS = [("[link]", " xxlink "), ("[url]", " xxlink "), ("[phone]", " xxphone "), ("[number]", _NUM_STANDIN),
                    ("[money]", " xxtien "), ("[date]", " xxngay "), ("[time]", " xxgio "), ("[name]", " xxten "),
                    ("[point]", " xxdiem "), ("[qc]", " xxqc "), ("[ad]", " xxqc "), ("[tb]", " thong bao ")]
_KH_V6 = re.compile(r"\b(quy kh|kh vui long)\b")


def normalize_vi6(text: str) -> str:
    """Dyv6.0: như normalize_vi + đưa hai kiểu che số (production / che mọi con số) về cùng dạng (xem chú thích ở trên)."""
    t = strip_diacritics(text).lower()
    t = _V6_QC_HEAD.sub(" xxqc ", t, count=1)
    for ph, tok in _V6_PLACEHOLDERS:
        t = t.replace(ph, tok)
    t = _REPEAT.sub(r"\1", t)
    t = _V6_MONEY.sub(" xxtien ", t)
    t = _V6_DATE.sub(" xxngay ", t)
    t = _V6_TIME.sub(" xxgio ", t)
    t = _V6_CODE.sub(" xxma ", t)
    t = _V6_DIGITS.sub(" xxso ", t)
    t = _KH_V6.sub(lambda m: m.group(1).replace("kh", "khach hang"), t)
    t = _KH_CUSTOMER.sub("khach hang ", t)
    t = _ABBR.sub(lambda m: ABBREVIATIONS[m.group(1)], t)
    return re.sub(r"\s+", " ", t).strip()
