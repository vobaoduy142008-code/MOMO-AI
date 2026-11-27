"""Chuẩn hoá tin nhắn trước khi đưa vào model (Dyv8.1) — gỡ các mẹo viết để né bộ lọc mà không làm mất nội dung.

1. Unicode NFKC: chữ full-width, chữ số kiểu khác ("①", "１") về dạng thường; tin gõ trên máy dùng dấu tách rời (NFD) về dạng dựng sẵn.
2. Bỏ ký tự vô hình (khoảng trắng độ rộng 0, dấu gạch mềm, ...) chèn giữa chữ để lách từ khóa.
3. Dãy từ 6 chữ số trở lên đọc bằng chữ ("mot khong hai ba bon nam ...") đổi thành chữ số, để bộ che thông tin bắt được số tài
   khoản / số điện thoại và model thấy đúng mẫu "chuyển tiền vào STK [số]" (QUESTION-39). Dưới 6 từ thì giữ nguyên, vì câu
   thường hiếm khi có 6 từ chỉ số liền nhau ("ba mẹ", "năm nay", "bay về" không bị đổi).

KHÔNG đổi chữ Cyrillic / Hy Lạp giống chữ Latin: link giả dạng "mоmо.vn" là dấu hiệu lừa đảo, đổi thành "momo.vn" sẽ làm mất dấu
hiệu đó. Dùng chung cho Dyv (chạy ở đây) và V4 (`chay_model_v4/trich_dac_trung_v4.py`), nên chỉ dùng thư viện chuẩn.
"""

from __future__ import annotations

import re
import unicodedata

VO_HINH = re.compile("[­͏؜ᅟᅠ឴឵᠎​-‏‪-‮⁠-⁤⁦-⁯﻿]")
_SO = {
    "0": ("khong", "không"),
    "1": ("mot", "một"),
    "2": ("hai",),
    "3": ("ba",),
    "4": ("bon", "bốn"),
    "5": ("nam", "năm"),
    "6": ("sau", "sáu"),
    "7": ("bay", "bảy", "bẩy"),
    "8": ("tam", "tám"),
    "9": ("chin", "chín"),
}
TU_SO = {w: d for d, ws in _SO.items() for w in ws}
SO_TU_TOI_THIEU = 6
_W = "|".join(sorted((re.escape(w) for w in TU_SO), key=len, reverse=True))
_DAY_SO = re.compile(rf"(?<!\w)(?:(?:{_W})[\s,.\-]+){{{SO_TU_TOI_THIEU - 1},}}(?:{_W})(?!\w)", re.IGNORECASE)
_TU = re.compile(rf"{_W}", re.IGNORECASE)


def _doi_day_so(m: re.Match) -> str:
    return "".join(TU_SO[w.lower()] for w in _TU.findall(m.group(0)))


def chuan_hoa(text: str) -> str:
    if not text:
        return text
    t = unicodedata.normalize("NFKC", str(text))
    t = VO_HINH.sub("", t)
    return _DAY_SO.sub(_doi_day_so, t)


if __name__ == "__main__":
    for s in ("CHUYEN NGAY 3TR VAO STK MOT KHONG HAI BA BON NAM SAU BAY TAM CHIN DE GIU SUAT",
              "chuyển vào số không chín không ba một hai ba bốn năm sáu nhé",
              "Bạn trúng thưởng​ iPhone 17", "Ba mẹ năm nay bay về quê, sau đó tám giờ tối mới tới",
              "Chúc mừng bạn trúng thưởng! Nhận tại mоmо.vn/qua"):
        print(repr(chuan_hoa(s)))
