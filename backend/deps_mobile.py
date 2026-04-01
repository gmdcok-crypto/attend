"""모바일 Bearer JWT에서 사원 id 추출."""

from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.database import Connection, DictCursor, get_db
from backend.mobile_jwt import decode_mobile_access_token

_mobile_bearer = HTTPBearer(auto_error=True)


def get_mobile_employee_id(
    cred: HTTPAuthorizationCredentials = Depends(_mobile_bearer),
    conn: Connection = Depends(get_db),
) -> int:
    try:
        payload = decode_mobile_access_token(cred.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.") from None

    if payload.get("typ") not in ("mobile_access", "mobile"):
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    try:
        emp_id = int(payload.get("sub") or 0)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.") from None

    cur = conn.cursor(DictCursor)
    cur.execute(
        "SELECT auth_status FROM employees WHERE id = %s LIMIT 1",
        (emp_id,),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="사원을 찾을 수 없습니다.")
    raw_auth = row.get("auth_status")
    if isinstance(raw_auth, (bytes, bytearray)):
        raw_auth = raw_auth.decode("ascii", errors="ignore")
    auth_s = str(raw_auth).strip() if raw_auth is not None else "X"
    if auth_s != "O":
        raise HTTPException(status_code=401, detail="인증이 해제되었습니다. 다시 로그인하세요.")
    return emp_id
