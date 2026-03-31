"""모바일 Bearer JWT에서 사원 id 추출."""

from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.mobile_jwt import decode_mobile_access_token

_mobile_bearer = HTTPBearer(auto_error=True)


def get_mobile_employee_id(cred: HTTPAuthorizationCredentials = Depends(_mobile_bearer)) -> int:
    try:
        payload = decode_mobile_access_token(cred.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.") from None

    if payload.get("typ") not in ("mobile_access", "mobile"):
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    try:
        return int(payload.get("sub") or 0)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.") from None
