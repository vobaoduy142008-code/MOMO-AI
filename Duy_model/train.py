#!/usr/bin/env python3
"""Train model thống nhất của Duy, từ đầu đến cuối, bằng một lệnh.

    python train.py                       # chọn cấu hình trên tập val + train bản ĐO (chưa thấy val_vi / test) -> mo_hinh/<phiên bản>/ban_do.joblib
    python train.py --release             # SAU KHI đã đo (danh_gia.py): train lại cùng cấu hình, thêm val_vi + test_vi_internal -> model.joblib
    python train.py --phien-ban Dyv12.0.2 # phiên bản mới (ghi thêm vào PHIEN_BAN.md)

Chọn cấu hình (không bao giờ nhìn test):
  1. alpha ∈ {1e-6 … 1e-3} × trọng số tin SMS thật ∈ {1, 3, 10}: giữ cấu hình có PR-AUC trên val_vi ≥ cao nhất − 0,002 (tối đa 4).
  2. Với các cấu hình còn lại: 5 phần out-of-fold chia theo mẫu trên tệp train v8; lấy PR-AUC (lừa đảo so với hợp lệ) cao nhất.
  3. Chênh dưới 0,001 thì lấy alpha lớn hơn, rồi trọng số nhỏ hơn.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
from sklearn.metrics import average_precision_score, log_loss
from sklearn.model_selection import GroupKFold

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from duy_model import du_lieu as DL  # noqa: E402
from duy_model import mo_hinh as MH  # noqa: E402

ALPHAS = (1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3)
TRONG_SO = (1, 3, 10)


def do(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return {"pr_auc": float(average_precision_score(y, p)), "log_loss": float(log_loss(y, p, labels=[0, 1])),
            "sai_05": float(((p >= 0.5).astype(int) != y).mean())}


def chon_cau_hinh(rows, val):
    norms = [r["norm"] for r in rows]
    tf = MH.tfidf().fit(norms)
    X, Xv = MH.dac_trung(tf, norms), MH.dac_trung(tf, [r["norm"] for r in val])
    y, yv = np.array([r["label"] for r in rows]), np.array([r["label"] for r in val])
    nguon = np.array([r["nguon"] for r in rows])
    cung = ~np.array([r["soft"] for r in rows])
    bang = []
    for w_that in TRONG_SO:
        w = MH.MoHinhDuy(trong_so_that=w_that).trong_so(rows)
        for a in ALPHAS:
            d = {"alpha": a, "trong_so_that": w_that, "val_vi": do(yv, MH.sgd(a, X, y, w).predict_proba(Xv)[:, 1])}
            bang.append(d)
            print(f"   alpha {a:.0e}, trọng số {w_that:>2}: PR-AUC val_vi {d['val_vi']['pr_auc']:.4f}", flush=True)
    tot = max(d["val_vi"]["pr_auc"] for d in bang)
    con = sorted([d for d in bang if d["val_vi"]["pr_auc"] >= tot - 0.002], key=lambda d: -d["val_vi"]["pr_auc"])[:4]
    i_v8 = np.flatnonzero(nguon == "v8")
    phan = [(i_v8[a], i_v8[b]) for a, b in GroupKFold(5).split(i_v8, groups=[rows[i]["template_id"] for i in i_v8])]
    k8 = (nguon == "v8") & cung
    for d in con:
        w = MH.MoHinhDuy(trong_so_that=d["trong_so_that"]).trong_so(rows)
        p = np.full(len(rows), np.nan)
        for _, i_ra in phan:
            hoc = np.setdiff1d(np.arange(len(rows)), i_ra)
            p[i_ra] = MH.sgd(d["alpha"], X[hoc], y[hoc], w[hoc]).predict_proba(X[i_ra])[:, 1]
        d["v8_oof"] = do(y[k8], p[k8])
        print(f"   bước 2: alpha {d['alpha']:.0e}, trọng số {d['trong_so_that']}: PR-AUC out-of-fold v8 {d['v8_oof']['pr_auc']:.4f}", flush=True)
    tot2 = max(d["v8_oof"]["pr_auc"] for d in con)
    chon = sorted([d for d in con if d["v8_oof"]["pr_auc"] >= tot2 - 0.001], key=lambda d: (-d["alpha"], d["trong_so_that"]))[0]
    return {"bang": bang, "chon": {"alpha": chon["alpha"], "trong_so_that": chon["trong_so_that"], "val_vi": chon["val_vi"],
                                   "v8_oof": chon["v8_oof"]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phien-ban", default="Dyv12.0.1")
    ap.add_argument("--release", action="store_true")
    args = ap.parse_args()
    out = os.path.join(HERE, "mo_hinh", args.phien_ban)
    os.makedirs(out, exist_ok=True)
    rows = DL.tap_train(release=args.release)
    print(f">> {len({(r['nguon'], r['id']) for r in rows})} tin, {len(rows)} dòng train", flush=True)
    f_ch = os.path.join(out, "cau_hinh.json")
    if args.release:
        ch = json.load(open(f_ch, encoding="utf-8"))["chon"]
    else:
        kq = chon_cau_hinh(rows, DL.tin_that("val_vi.csv", train=False))
        json.dump(kq, open(f_ch, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        ch = kq["chon"]
        print(f">> chọn alpha {ch['alpha']:.0e}, trọng số tin thật {ch['trong_so_that']}", flush=True)
    m = MH.MoHinhDuy(ch["alpha"], ch["trong_so_that"], args.phien_ban).fit(rows)
    m.thong_tin.update({"release": args.release, "so_tin_theo_nguon": {n: len({r["id"] for r in rows if r["nguon"] == n})
                                                                         for n in ("that", "mo_phong", "muc_b", "bo_29", "v8")}})
    ten = "model.joblib" if args.release else "ban_do.joblib"
    m.luu(os.path.join(out, ten))
    if not args.release:   # % out-of-fold (đã hiệu chỉnh) của tệp train v8, để đo bias (tin đã học / chưa học) ở danh_gia.py
        with open(os.path.join(out, "oof_v8_train.csv"), "w", encoding="utf-8") as f:
            f.write("id,nhan,p_oof\n")
            da = set()
            for r, p in zip(rows, m.oof, strict=True):
                if r["nguon"] == "v8" and r["id"] not in da:
                    da.add(r["id"])
                    f.write(f"{r['id']},{r['nhan']},{p:.6f}\n")
    print(f">> đã lưu {os.path.join('mo_hinh', args.phien_ban, ten)}")


if __name__ == "__main__":
    main()
