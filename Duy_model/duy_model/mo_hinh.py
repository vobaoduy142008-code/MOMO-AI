"""MoHinhDuy — một model thống nhất, train từ đầu đến cuối bằng một lệnh (train.py).

    tin -> xu_ly.chuan_bi -> [TF-IDF từ 1–2 gram + ký tự 2–5 gram] + [30 cờ dấu hiệu v6 × 0,3]
        -> SGD log-loss (trọng số lớp cân bằng; tin SMS thật nhân trọng số; tin nghi ngờ = nhãn mềm 0,5)
        -> hiệu chỉnh Platt trên dự đoán out-of-fold chia theo mẫu câu -> % khả năng lừa đảo (1–99%)
        -> 3 mức D-20: từ 70% "lừa đảo", 30–69% "nghi ngờ", dưới 30% "chưa thấy dấu hiệu rõ".

Không có mức "an toàn". File model chỉ chứa đối tượng scikit-learn + số thực (không pickle lớp tự viết), nạp bằng MoHinhDuy.nap().
"""

from __future__ import annotations

import os
import time

import joblib
import numpy as np
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import FeatureUnion

from . import xu_ly

NGUONG_CANH_BAO, NGUONG_LUA_DAO = 0.30, 0.70
MUC = {
    "lua_dao": "Lừa đảo — đừng chuyển tiền, đừng bấm link, đừng đọc mã OTP",
    "nghi_ngo": "Nghi ngờ — có dấu hiệu rủi ro, hãy kiểm tra lại qua kênh chính thức",
    "hop_le": "Chưa thấy dấu hiệu rõ — vẫn cần cẩn trọng",
}
FLAG_SCALE = 0.3
SEED = 0


def tfidf():
    return FeatureUnion([
        ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True, token_pattern=r"(?u)\b\w+\b")),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3, sublinear_tf=True, max_features=60000)),
    ])


def dac_trung(tf, norms):
    return sp.hstack([tf.transform(norms), sp.csr_matrix(xu_ly.co_v6(norms) * FLAG_SCALE)]).tocsr()


def sgd(alpha, X, y, w):
    cw = len(y) / (2 * np.bincount(y, minlength=2))
    return SGDClassifier(loss="log_loss", alpha=alpha, class_weight={0: float(cw[0]), 1: float(cw[1])}, max_iter=50, tol=None,
                         random_state=SEED).fit(X, y, sample_weight=w)


def _logit(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def muc_cua(p: float) -> str:
    return "lua_dao" if p >= NGUONG_LUA_DAO else ("nghi_ngo" if p >= NGUONG_CANH_BAO else "hop_le")


class MoHinhDuy:
    def __init__(self, alpha=1e-5, trong_so_that=10.0, phien_ban="Dyv12.0.1"):
        self.alpha, self.trong_so_that, self.phien_ban = float(alpha), float(trong_so_that), phien_ban
        self.tf = self.clf = None
        self.platt = None          # (hệ số, chặn) của hồi quy logistic trên logit(% SGD)
        self.thong_tin = {}

    # ---------------- train ----------------
    def trong_so(self, rows):
        return np.array([r["w0"] * (self.trong_so_that if r["nguon"] == "that" else 1.0) for r in rows])

    def fit(self, rows, so_phan=5, log=print):
        """rows: dict có norm, label (0/1), w0, nguon, template_id, soft. Trả về self; self.oof = % out-of-fold đã hiệu chỉnh."""
        t0 = time.time()
        norms = [r["norm"] for r in rows]
        y = np.array([r["label"] for r in rows])
        w = self.trong_so(rows)
        oof = np.zeros(len(rows))
        for k, (i_tr, i_te) in enumerate(GroupKFold(n_splits=so_phan).split(rows, groups=[r["template_id"] for r in rows]), 1):
            tf = tfidf().fit([norms[i] for i in i_tr])
            clf = sgd(self.alpha, dac_trung(tf, [norms[i] for i in i_tr]), y[i_tr], w[i_tr])
            oof[i_te] = clf.predict_proba(dac_trung(tf, [norms[i] for i in i_te]))[:, 1]
            log(f"   out-of-fold phần {k}/{so_phan} ({time.time() - t0:.0f} giây)")
        lr = LogisticRegression(C=1e6).fit(_logit(oof).reshape(-1, 1), y, sample_weight=w)
        self.platt = (float(lr.coef_[0, 0]), float(lr.intercept_[0]))
        self.oof_tho, self.oof = oof, self._hieu_chinh(oof)
        self.tf = tfidf().fit(norms)
        self.clf = sgd(self.alpha, dac_trung(self.tf, norms), y, w)
        self.thong_tin.update({"so_dong_train": len(rows), "thoi_gian_giay": round(time.time() - t0)})
        log(f">> train xong {len(rows)} dòng ({time.time() - t0:.0f} giây)")
        return self

    # ---------------- chạy ----------------
    def _hieu_chinh(self, p_tho):
        a, b = self.platt
        return np.clip(1 / (1 + np.exp(-(a * _logit(p_tho) + b))), 0.01, 0.99)

    def phan_tram_norm(self, norms):
        return self._hieu_chinh(self.clf.predict_proba(dac_trung(self.tf, list(norms)))[:, 1])

    def phan_tram(self, texts):
        """Danh sách tin gốc -> mảng % khả năng lừa đảo (0,01–0,99)."""
        return self.phan_tram_norm([xu_ly.chuan_bi(t) for t in texts])

    def du_doan(self, text: str) -> dict:
        """Một tin gốc -> kết quả cho API / giao diện."""
        norm = xu_ly.chuan_bi(text)
        p = float(self.phan_tram_norm([norm])[0])
        co = xu_ly.co_v6([norm])[0]
        muc = muc_cua(p)
        return {"phan_tram": round(p * 100), "muc": muc, "ket_luan": MUC[muc],
                "dau_hieu": [xu_ly.NHAN_CO[t] for t, v in zip(xu_ly.TEN_CO, co, strict=True) if v],
                "phien_ban": self.phien_ban}

    # ---------------- lưu / nạp ----------------
    def luu(self, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        joblib.dump({"phien_ban": self.phien_ban, "alpha": self.alpha, "trong_so_that": self.trong_so_that, "tf": self.tf,
                     "clf": self.clf, "platt": self.platt, "flag_scale": FLAG_SCALE, "thong_tin": self.thong_tin},
                    path, compress=("xz", 6))

    @classmethod
    def nap(cls, path):
        d = joblib.load(path)
        m = cls(d["alpha"], d["trong_so_that"], d["phien_ban"])
        m.tf, m.clf, m.platt, m.thong_tin = d["tf"], d["clf"], tuple(d["platt"]), d.get("thong_tin", {})
        return m
