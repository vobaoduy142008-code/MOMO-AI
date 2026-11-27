#!/usr/bin/env python3
"""Đo bản ĐO của một phiên bản (mo_hinh/<phiên bản>/ban_do.joblib) MỘT lần trên các bộ test, kèm bias / variance.

    python danh_gia.py                        # Dyv12.0.1
    python danh_gia.py --phien-ban Dyv12.0.2
    -> ket_qua/danh_gia_<phiên bản>.md, .json (chỉ số đo; không có nội dung tin)

Mốc 30% (D-20): tin lừa đảo / nghi ngờ phải từ 30%, tin hợp lệ dưới 30%. 3 mức: lừa đảo từ 70%, nghi ngờ 30–69%, hợp lệ dưới 30%.
Bias = sai trên tin SMS thật ĐÃ học; variance = tin SMS thật chưa học sai thêm; lệch dữ liệu = tin kiểu khác (bộ v8) sai thêm.
So sánh: Dyv10.1 và Dyv12.1 (bản gộp V4C + Dyv cũ) lấy từ ket_qua/tham_chieu_Dyv10.1_Dyv12.1.json (bản đo, cùng các bộ test).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from duy_model import du_lieu as DL  # noqa: E402
from duy_model import mo_hinh as MH  # noqa: E402


def chi_so(rows, p):
    y3 = np.array([r["y3"] for r in rows])
    y = (y3 > 0).astype(int)
    canh = p >= MH.NGUONG_CANH_BAO
    muc = np.where(p >= MH.NGUONG_LUA_DAO, 1.0, np.where(canh, 0.5, 0.0))
    return {"n": len(rows), "acc30": float((canh == (y == 1)).mean()), "acc3": float((muc == y3).mean()),
            "sai30": int((canh != (y == 1)).sum()), "bat30": int((canh & (y == 1)).sum()), "n_lua": int(y.sum()),
            "nham30": int((canh & (y == 0)).sum()), "n_hop_le": int((y == 0).sum()),
            "auc": float(roc_auc_score(y, p)) if 0 < y.sum() < len(y) else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phien-ban", default="Dyv12.0.1")
    args = ap.parse_args()
    m = MH.MoHinhDuy.nap(os.path.join(HERE, "mo_hinh", args.phien_ban, "ban_do.joblib"))
    test = DL.tin_that("test_vi_internal.csv", train=False, bo_da_doc=True)
    bo = {"Tin thật, nửa dev": [r for r in test if DL.nua_test(r["id"]) == "dev"],
          "Tin thật, nửa giữ lại": [r for r in test if DL.nua_test(r["id"]) == "giu_lai"],
          "Mục B, file test": DL.muc_b("muc_b_test.csv", train=False),
          "Bộ 29 kiểu, phần test": DL.bo_29("test", train=False),
          "v8 public_test": DL.v8("public_test", train=False),
          "v8 private_test": DL.v8("private_test", train=False)}
    kq = {"phien_ban": args.phien_ban, "bo": {}}
    for t, rr in bo.items():
        kq["bo"][t] = chi_so(rr, m.phan_tram_norm([r["norm"] for r in rr]))
    s = [kq["bo"][t]["sai30"] for t in ("Tin thật, nửa dev", "Tin thật, nửa giữ lại")]
    kq["tin_that_gop"] = {"n": len(test), "sai30": sum(s)}

    # bias / variance / lệch dữ liệu (mốc 30%)
    hoc = DL.tin_that("train_vi_only.csv", train=False)
    sai_hoc = 1 - chi_so(hoc, m.phan_tram_norm([r["norm"] for r in hoc]))["acc30"]
    sai_chua = sum(s) / len(test)
    pub_moi = [r for r in bo["v8 public_test"] if r["meta"]["nguon_chu_de"] != "test_cu"]
    sai_pub = 1 - chi_so(pub_moi, m.phan_tram_norm([r["norm"] for r in pub_moi]))["acc30"]
    sai_pri = 1 - kq["bo"]["v8 private_test"]["acc30"]
    oof = [ln.strip().split(",") for ln in open(os.path.join(HERE, "mo_hinh", args.phien_ban, "oof_v8_train.csv"), encoding="utf-8")][1:]
    y_o = np.array([DL.Y3[n] > 0 for _, n, _ in oof])
    sai_v8_oof = float(((np.array([float(p) for *_, p in oof]) >= MH.NGUONG_CANH_BAO) != y_o).mean())
    kq["bias_variance"] = {"bias": sai_hoc, "variance": sai_chua - sai_hoc, "sai_tin_that_chua_hoc": sai_chua,
                           "lech_v8_public_cau_moi": sai_pub - sai_chua, "lech_v8_private": sai_pri - sai_chua,
                           "sai_v8_train_out_of_fold": sai_v8_oof, "sai_v8_public_cau_moi": sai_pub, "sai_v8_private": sai_pri}
    json.dump(kq, open(os.path.join(HERE, "ket_qua", f"danh_gia_{args.phien_ban}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    ref = json.load(open(os.path.join(HERE, "ket_qua", "tham_chieu_Dyv10.1_Dyv12.1.json"), encoding="utf-8"))

    def pt(x):
        return "–" if x is None else f"{x * 100:.1f}%"

    v = args.phien_ban
    L = [f"# {v}: kết quả đo (bản đo, một lần)\n",
         "Tạo bằng `python danh_gia.py`. Dyv10.1 và Dyv12.1 là bản gộp V4C + Dyv cũ (bản đo), cùng các bộ test. Bộ mục B, 29 kiểu, v8 là tin "
         "mô phỏng: chỉ để so giữa các bản, không phải độ chính xác thật.\n",
         f"| Bộ | n | Mốc 30%: Dyv10.1 / Dyv12.1 / **{v}** | 3 mức: Dyv10.1 / Dyv12.1 / **{v}** | Bắt lừa đảo ({v}) | Nhầm hợp lệ ({v}) | "
         f"ROC-AUC ({v}) |", "|---|---|---|---|---|---|---|"]
    for t, d in kq["bo"].items():
        r = ref.get(t, {})
        a, b = r.get("Dyv10.1", {}), r.get("Dyv12.1", {})
        L.append(f"| {t} | {d['n']} | {pt(a.get('acc30'))} / {pt(b.get('acc30'))} / **{pt(d['acc30'])}** | {pt(a.get('acc3'))} / "
                 f"{pt(b.get('acc3'))} / **{pt(d['acc3'])}** | {d['bat30']}/{d['n_lua']} | {d['nham30']}/{d['n_hop_le']} | "
                 f"{'–' if d['auc'] is None else f'{d['auc']:.3f}'} |")
    g = ref["gop_hai_nua"]["sai"]
    bv = kq["bias_variance"]
    L += ["", f"Tin SMS thật, gộp hai nửa ({len(test)} tin): sai Dyv10.1 {g['Dyv10.1']}, Dyv12.1 {g['Dyv12.1']}, **{v} {sum(s)}**.", "",
          "## Bias / variance (mốc 30%)\n",
          f"- **Bias** (sai trên {len(hoc)} tin SMS thật đã học): **{bv['bias'] * 100:.1f}%**",
          f"- **Variance** (tin SMS thật chưa học sai thêm): **{bv['variance'] * 100:+.1f} điểm** (sai {bv['sai_tin_that_chua_hoc'] * 100:.1f}%)",
          f"- **Lệch dữ liệu**: v8 public câu mới {bv['lech_v8_public_cau_moi'] * 100:+.1f} điểm (sai {bv['sai_v8_public_cau_moi'] * 100:.1f}%), "
          f"v8 private {bv['lech_v8_private'] * 100:+.1f} điểm (sai {bv['sai_v8_private'] * 100:.1f}%)",
          f"- Tệp train v8, out-of-fold chia theo mẫu (mẫu câu chưa học): sai {bv['sai_v8_train_out_of_fold'] * 100:.1f}%"]
    open(os.path.join(HERE, "ket_qua", f"danh_gia_{v}.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
