"""Xử lý tin trước khi vào model — dùng chung lúc train và lúc chạy (API), để hai bên giống hệt nhau.

Thứ tự: chuẩn hoá đầu vào (chữ đồng hình, ký tự ẩn, khoảng trắng) → che link / số điện thoại / dãy số dài → chuẩn hoá vi6
(viết tắt, teencode, mọi cách che số về một dạng).
"""

from __future__ import annotations

import re

from ._input_normalizer import chuan_hoa
from ._red_flags import ALL_FLAG_NAMES_V6, FLAG_LABELS, FLAG_SETS
from ._vn_text import normalize_vi6

RE_LINK = re.compile(r"(https?://\S+|www\.\S+|\b[\w-]+(?:\.[\w-]+)*\.(?:com\.vn|vn|com|net|top|xyz|vip|online|site|cc|icu|shop|info|club|ly|at)"
                     r"(?:/\S*)?)", re.I)
RE_PHONE = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.]?\d){9}(?!\d)")
RE_LONG = re.compile(r"(?<!\d)\d{7,}(?!\d)")
RE_HOTLINE = re.compile(r"^(1900|1800)\d{4,6}$")

co_v6 = FLAG_SETS["v6"][0]          # hàm: danh sách văn bản đã chuẩn hoá -> ma trận cờ dấu hiệu (0/1)
TEN_CO = list(ALL_FLAG_NAMES_V6)
NHAN_CO = {k: FLAG_LABELS.get(k, k) for k in TEN_CO}


def che(text: str) -> str:
    """Che link, số điện thoại, dãy số dài (giữ tổng đài 1900/1800) — để model không học thuộc số cụ thể."""
    def _link(m):
        s, duoi = m.group(0), ""
        while s and s[-1] in ".,;:!?)":
            duoi, s = s[-1] + duoi, s[:-1]
        return "[LINK]" + duoi
    t = RE_LINK.sub(_link, text)
    t = RE_PHONE.sub("[PHONE]", t)
    return RE_LONG.sub(lambda m: m.group(0) if RE_HOTLINE.match(m.group(0)) else "[NUMBER]", t)


def chuan_bi(text: str) -> str:
    """Tin gốc (như người dùng dán) -> chuỗi đưa vào model."""
    return normalize_vi6(che(chuan_hoa(text or "")))


def chuan_bi_da_che(text: str) -> str:
    """Tin đã che sẵn (data_v6) -> chuỗi đưa vào model."""
    return normalize_vi6(text or "")
