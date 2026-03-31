"""모바일 앱용 JWT (HS256)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt

_ALGO = "HS256"


def _secret() -> str:
    s = (os.getenv("JWT_SECRET") or "").strip()
    if s:
        return s
    # 로컬 개발 편의 — 운영에서는 반드시 환경 변수 JWT_SECRET 설정
    return "attend-dev-only-insecure-jwt-secret-change-in-production"


def create_mobile_access_token(employee_id: int, employee_no: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=int(os.getenv("JWT_EXPIRE_DAYS", "30")))
    payload = {
        "sub": str(employee_id),
        "emp_no": employee_no.strip(),
        "typ": "mobile",
        "exp": expire,
    }
    return jwt.encode(payload, _secret(), algorithm=_ALGO)


def decode_mobile_access_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=[_ALGO])
