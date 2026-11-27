#!/usr/bin/env python3
"""Thử model từ dòng lệnh.

    python du_doan.py "Tài khoản của bạn bị khoá, bấm vào link để xác minh"
    python du_doan.py --phien-ban Dyv12.0.1 --ban-do "..."     # dùng bản đo thay vì bản release
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from duy_model.mo_hinh import MoHinhDuy  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("van_ban", nargs="+")
ap.add_argument("--phien-ban", default="Dyv12.0.1")
ap.add_argument("--ban-do", action="store_true")
a = ap.parse_args()
m = MoHinhDuy.nap(os.path.join(HERE, "mo_hinh", a.phien_ban, "ban_do.joblib" if a.ban_do else "model.joblib"))
for t in a.van_ban:
    print(json.dumps(m.du_doan(t), ensure_ascii=False))
