#!/usr/bin/env python3
"""API của model Duy — để backend / frontend của trang web gọi.

    pip install -r requirements.txt
    uvicorn api:app --port 8001            # chạy trong thư mục Duy_model/

    GET  /suc-khoe                         -> {"ok": true, "phien_ban": "Dyv12.0.1"}
    POST /kiem-tra  {"van_ban": "..."}     -> {"phan_tram": 87, "muc": "lua_dao", "ket_luan": "...", "dau_hieu": [...], "phien_ban": "..."}

Biến môi trường: DUY_MODEL_PHIEN_BAN (mặc định Dyv12.0.1), DUY_MODEL_FILE (mặc định mo_hinh/<phiên bản>/model.joblib),
DUY_MODEL_CORS (danh sách origin, cách nhau bởi dấu phẩy; mặc định không mở CORS).
Không có mức "an toàn": dưới 30% là "Chưa thấy dấu hiệu rõ — vẫn cần cẩn trọng". API không lưu tin người dùng gửi.
"""

from __future__ import annotations

import os
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from duy_model.mo_hinh import MoHinhDuy  # noqa: E402

PHIEN_BAN = os.environ.get("DUY_MODEL_PHIEN_BAN", "Dyv12.0.1")
FILE = os.environ.get("DUY_MODEL_FILE", os.path.join(HERE, "mo_hinh", PHIEN_BAN, "model.joblib"))
TOI_DA = 5000                      # số ký tự tối đa mỗi lần kiểm tra

model = MoHinhDuy.nap(FILE)
app = FastAPI(title="Model Duy — kiểm tra tin nhắn lừa đảo", version=PHIEN_BAN)
if os.environ.get("DUY_MODEL_CORS"):
    app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in os.environ["DUY_MODEL_CORS"].split(",")],
                       allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


class YeuCau(BaseModel):
    van_ban: str = Field(..., min_length=1, max_length=TOI_DA, description="Tin nhắn / đoạn hội thoại cần kiểm tra")


@app.get("/suc-khoe")
def suc_khoe():
    return {"ok": True, "phien_ban": model.phien_ban}


@app.post("/kiem-tra")
def kiem_tra(yc: YeuCau):
    if not yc.van_ban.strip():
        raise HTTPException(status_code=422, detail="Tin nhắn trống")
    return model.du_doan(yc.van_ban)
