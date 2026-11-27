#!/usr/bin/env python3
"""Kiểm tra chất lượng 3 tệp bộ v8 (train / public_test / private_test) trước khi dùng hay đưa ban giám khảo xem.

    python kiem_tra_du_lieu.py   -> ket_qua/kiem_tra_du_lieu_v8.md (chỉ số đếm, không in nội dung tin)

Kiểm: đủ cột, không trống, nhãn hợp lệ; phân bố nhãn / độ khó / dạng tin; trùng mã và trùng câu trong và giữa các tệp; mẫu câu
(template) không dùng chung giữa train và test; câu gần giống nhau giữa test và train (rò rỉ); số điện thoại, email, dãy số dài
nằm ngoài dải giả.
"""

from __future__ import annotations

import csv
import os
import re
import unicodedata
from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.join(HERE, "du_lieu", "v8")
TEP = {"train": os.path.join(V8, "sms_v8_train.csv"), "public_test": os.path.join(V8, "sms_v8_public_test.csv"),
       "private_test": os.path.join(V8, "private_KHONG_TRAIN", "sms_v8_private_test.csv")}
COT = ("id", "text", "text_raw", "nhan", "muc_do", "dang", "kenh", "template_id", "chu_de")
RE_PHONE = re.compile(r"(?<!\d)(0[35789]\d[\s.]?\d{3}[\s.]?\d{3,4})(?!\d)")
PHONE_GIA = re.compile(r"^0(900|911|922|933|944|388|777)000\d{3}$")
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
RE_SO_DAI = re.compile(r"(?<!\d)\d{9,16}(?!\d)")
NGUONG_GAN = 0.90


def n(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s or "").lower()).strip()


def main():
    d = {k: list(csv.DictReader(open(p, encoding="utf-8-sig"))) for k, p in TEP.items()}
    L = ["# Kiểm tra chất lượng bộ v8 (train / public_test / private_test)\n", "Tạo bằng `python kiem_tra_du_lieu.py`. Chỉ đếm, không in nội "
         "dung tin.\n", "## 1. Cấu trúc và phân bố\n", "| Tệp | Số tin | Thiếu cột | Tin trống | Nhãn lạ | Lừa đảo / nghi ngờ / hợp lệ | Độ khó | Dạng tin |",
         "|---|---|---|---|---|---|---|---|"]
    loi = []
    for k, rows in d.items():
        thieu = [c for c in COT if c not in rows[0]]
        trong = sum(not (r.get("text_raw") or "").strip() for r in rows)
        la = sum(r["nhan"] not in ("lua_dao", "nghi_ngo", "hop_le") for r in rows)
        nh = Counter(r["nhan"] for r in rows)
        L.append(f"| {k} | {len(rows)} | {', '.join(thieu) or 'không'} | {trong} | {la} | {nh['lua_dao']} / {nh['nghi_ngo']} / {nh['hop_le']} | "
                 + ", ".join(f"{a} {b}" for a, b in sorted(Counter(r['muc_do'] for r in rows).items())) + " | "
                 + ", ".join(f"{a} {b}" for a, b in sorted(Counter(r['dang'] for r in rows).items())) + " |")
        loi += [f"{k}: thiếu cột {thieu}"] * bool(thieu) + [f"{k}: {trong} tin trống"] * bool(trong) + [f"{k}: {la} nhãn lạ"] * bool(la)

    L += ["", "## 2. Trùng lặp và rò rỉ giữa các tệp\n", "| Kiểm | train | public_test | private_test |", "|---|---|---|---|"]
    ma = {k: Counter(r["id"] for r in rows) for k, rows in d.items()}
    cau = {k: Counter(n(r["text_raw"]) for r in rows) for k, rows in d.items()}
    L.append("| Mã tin trùng trong tệp | " + " | ".join(str(sum(v > 1 for v in ma[k].values())) for k in d) + " |")
    L.append("| Câu trùng nguyên văn trong tệp | " + " | ".join(str(sum(v - 1 for v in cau[k].values() if v > 1)) for k in d) + " |")
    cap = [("train", "public_test"), ("train", "private_test"), ("public_test", "private_test")]
    L += ["", "| Cặp tệp | Mã tin chung | Câu chung (nguyên văn) | Mẫu câu (template) chung | Câu test gần giống câu train (cosine ≥ 0,9) |",
          "|---|---|---|---|---|"]
    for a, b in cap:
        ma_chung = len(set(ma[a]) & set(ma[b]))
        cau_chung = len(set(cau[a]) & set(cau[b]))
        mau_chung = len({r["template_id"] for r in d[a]} & {r["template_id"] for r in d[b]})
        vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_df=0.05, sublinear_tf=True).fit([n(r["text_raw"]) for r in d[a]])
        A, B = vec.transform([n(r["text_raw"]) for r in d[a]]), vec.transform([n(r["text_raw"]) for r in d[b]])
        gan = 0
        for i in range(0, B.shape[0], 500):
            gan += int((np.asarray((B[i:i + 500] @ A.T).max(axis=1).todense()).ravel() >= NGUONG_GAN).sum())
        L.append(f"| {a} ↔ {b} | {ma_chung} | {cau_chung} | {mau_chung} | {gan} |")
        if a == "train" and (cau_chung or mau_chung or gan):
            loi.append(f"{a} ↔ {b}: {cau_chung} câu chung, {mau_chung} mẫu chung, {gan} câu gần giống")

    L += ["", "## 3. Dữ liệu cá nhân (Điều 12.4 thể lệ)\n",
          "| Tệp | Số điện thoại | Ngoài dải giả `09xx 000 xxx` | Email | Dãy 9–16 chữ số |", "|---|---|---|---|---|"]
    for k, rows in d.items():
        t = [r["text_raw"] for r in rows]
        ph = [re.sub(r"\D", "", m) for x in t for m in RE_PHONE.findall(x)]
        ngoai = [p for p in ph if not PHONE_GIA.match(p)]
        em = [m for x in t for m in RE_EMAIL.findall(x)]
        so = [m for x in t for m in RE_SO_DAI.findall(x)]
        L.append(f"| {k} | {len(ph)} | {len(ngoai)} | {len(em)} (tên miền: {', '.join(sorted({e.split('@')[1] for e in em})) or '–'}) | "
                 f"{len(so)} |")
        loi += [f"{k}: {len(ngoai)} số điện thoại ngoài dải giả"] * bool(ngoai)
    L += ["", "## Kết luận\n", "**Không phát hiện lỗi.**" if not loi else "Cần xem:\n" + "\n".join(f"- {x}" for x in loi)]
    open(os.path.join(HERE, "ket_qua", "kiem_tra_du_lieu_v8.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
