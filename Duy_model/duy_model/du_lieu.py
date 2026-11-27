"""Đọc dữ liệu trong thư mục du_lieu/ thành các dòng train/đo cùng một dạng.

Mỗi dòng: id, norm (đã qua xu_ly), label (0/1), w0 (1; 0,5 cho tin nghi ngờ), soft (tin nghi ngờ), template_id (để chia theo mẫu câu),
nguon (that / mo_phong / muc_b / bo_29 / v8), nhan (lua_dao / nghi_ngo / hop_le), y3 (1 / 0,5 / 0).
Tin nghi ngờ được TRAIN bằng nhãn mềm: tách thành 2 dòng nhãn 1 và 0, mỗi dòng trọng số 0,5.
"""

from __future__ import annotations

import csv
import hashlib
import os

from . import xu_ly

GOC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "du_lieu")
DA_DOC = {"p0_vi_COM_2335"}       # tin test thật đã bị đọc nội dung khi xem cấu trúc cột (25/11) -> không dùng để đo
Y3 = {"lua_dao": 1.0, "nghi_ngo": 0.5, "hop_le": 0.0}


def _doc(*p):
    with open(os.path.join(GOC, *p), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _dong(id_, norm, nhan, template, nguon, out, train=True):
    """Thêm dòng; với train, tin nghi ngờ thành 2 dòng nhãn mềm."""
    base = {"id": id_, "norm": norm, "template_id": template, "nguon": nguon, "nhan": nhan, "y3": Y3[nhan]}
    if train and nhan == "nghi_ngo":
        out += [{**base, "label": lab, "w0": 0.5, "soft": True} for lab in (1, 0)]
    else:
        out.append({**base, "label": int(Y3[nhan] > 0), "w0": 1.0, "soft": False})


def tin_that(file, train=True, bo_da_doc=False):
    """Tin SMS thật (du_lieu/that/, nguồn Vietnamese Quality-Assured SMS Scam Dataset, CC BY 4.0)."""
    out = []
    for r in _doc("that", file):
        if not (r.get("text") or "").strip() or str(r.get("label")).strip() not in ("0", "1"):
            continue
        if bo_da_doc and r["id"] in DA_DOC:
            continue
        _dong(r["id"], xu_ly.chuan_bi(r["text"]), "lua_dao" if r["label"].strip() == "1" else "hop_le", "THAT_" + r["id"], "that", out, train)
    return out


def nua_test(row_id):
    """Chia test_vi_internal thành 2 nửa cố định (dev / giu_lai) như các bản Dyv trước."""
    return "dev" if int(hashlib.md5(row_id.encode("utf-8")).hexdigest(), 16) % 2 == 0 else "giu_lai"


def data_v6():
    """Tin mô phỏng data_v6 (đã che sẵn, có cả tiếng Anh); dùng hết cho train."""
    out = []
    for r in _doc("mo_phong", "data_v6.csv"):
        _dong(r["id"], xu_ly.chuan_bi_da_che(r["text"]), r.get("nhan") or ("lua_dao" if r["label"] == "1" else "hop_le"),
              r["template_id"], "mo_phong", out)
    return out


def muc_b(file="muc_b_train.csv", train=True):
    out = []
    for r in _doc("mo_phong", file):
        _dong("B_" + r["id"], xu_ly.chuan_bi(r["text"]), "lua_dao" if r["label"] == "1" else "hop_le", "B_" + r["template_id"], "muc_b",
              out, train)
    return out


def bo_29(split, train=True):
    out = []
    for r in _doc("mo_phong", "bo_29_kieu.csv"):
        if r["split"] == split:
            _dong("V7_" + r["id"], xu_ly.chuan_bi(r["text_raw"]), r["nhan"], "V7_" + r["template_id"], "bo_29", out, train)
    return out


def v8(ten, train=True):
    """ten: 'train', 'public_test' hoặc 'private_test' (private chỉ để đo, KHÔNG BAO GIỜ train)."""
    if ten == "private_test" and train:
        raise ValueError("private_test chỉ dùng để đo, không train")
    p = ("v8", "private_KHONG_TRAIN", "sms_v8_private_test.csv") if ten == "private_test" else ("v8", f"sms_v8_{ten}.csv")
    out = []
    for r in _doc(*p):
        _dong(r["id"], xu_ly.chuan_bi(r["text_raw"]), r["nhan"], r["template_id"], "v8", out, train)
        out[-1]["meta"] = r if not train else None
    return out


def tap_train(release=False):
    """Toàn bộ dữ liệu train của model. release=True: thêm val_vi và test_vi_internal (chỉ sau khi đã đo)."""
    rows = (data_v6() + tin_that("train_vi_only.csv") + muc_b("muc_b_train.csv") + muc_b("muc_b_train_them_lua_dao.csv")
            + bo_29("train") + v8("train"))
    if release:
        rows += tin_that("val_vi.csv") + tin_that("test_vi_internal.csv")
    return rows
