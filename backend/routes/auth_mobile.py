"""모바일 앱 — 최초 비밀번호 설정 · 로그인 · JWT"""

from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from backend.database import Connection, DictCursor, get_db
from backend.admin_events_bus import publish_employee_auth_changed
from backend.mobile_jwt import (
    create_mobile_access_token,
    create_mobile_refresh_token,
    decode_mobile_access_token,
    decode_mobile_refresh_token,
)
from backend.passwords import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

bearer_scheme = HTTPBearer(auto_error=True)


class FirstPasswordBody(BaseModel):
    employee_no: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginBody(BaseModel):
    employee_no: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    name: Optional[str] = Field(
        default=None,
        description="최초 로그인(비밀번호 미설정) 시 사원관리 등록 성명과 동일하게 입력.",
    )


class RefreshBody(BaseModel):
    refresh_token: str = Field(..., min_length=1)


def _now_utc_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _refresh_expire_at() -> datetime:
    days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "14"))
    return _now_utc_naive() + timedelta(days=days)


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _issue_tokens(conn: Connection, emp_id: int, employee_no: str) -> dict:
    access = create_mobile_access_token(emp_id, employee_no)
    jti = secrets.token_urlsafe(24)
    refresh = create_mobile_refresh_token(emp_id, employee_no, jti=jti)
    token_hash = _hash_refresh_token(refresh)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO mobile_refresh_tokens (employee_id, token_hash, expires_at)
        VALUES (%s, %s, %s)
        """,
        (emp_id, token_hash, _refresh_expire_at()),
    )
    conn.commit()
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "access_expires_in": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")) * 60,
    }


def _serialize_me(row: dict) -> dict:
    hire = row.get("hire_date")
    if hasattr(hire, "isoformat"):
        hire = hire.isoformat()
    raw_auth = row.get("auth_status")
    if isinstance(raw_auth, (bytes, bytearray)):
        raw_auth = raw_auth.decode("ascii", errors="ignore")
    auth_s = str(raw_auth).strip() if raw_auth is not None else "X"
    if auth_s not in ("O", "X"):
        auth_s = "X"
    return {
        "id": int(row["id"]),
        "employee_no": row["employee_no"],
        "name": row["name"],
        "department_name": row.get("department_name"),
        "hire_date": hire,
        "status": row["status"],
        "auth_status": auth_s,
    }


@router.post("/first-password")
def set_first_password(body: FirstPasswordBody, conn: Connection = Depends(get_db)) -> dict:
    """미등록(해시 없음) 사원만: 사번·성명 확인 후 비밀번호 설정 및 인증 완료."""
    no = body.employee_no.strip()
    name = body.name.strip()
    cur = conn.cursor(DictCursor)
    cur.execute(
        """
        SELECT id, employee_no, name, password_hash, auth_status
        FROM employees
        WHERE employee_no = %s
        LIMIT 1
        """,
        (no,),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="등록된 사번이 없습니다.")
    if (row.get("name") or "").strip() != name:
        raise HTTPException(status_code=400, detail="이름이 일치하지 않습니다.")
    if row.get("password_hash"):
        raise HTTPException(status_code=400, detail="이미 비밀번호가 설정되어 있습니다. 로그인을 이용하세요.")

    emp_id = int(row["id"])
    pwd_hash = hash_password(body.password)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE employees
        SET password_hash=%s, auth_status='O'
        WHERE id=%s
        """,
        (pwd_hash, emp_id),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=500, detail="저장에 실패했습니다.")
    publish_employee_auth_changed(emp_id)

    tokens = _issue_tokens(conn, emp_id, row["employee_no"])
    return {
        "ok": True,
        **tokens,
        "employee_no": row["employee_no"],
        "name": (row.get("name") or "").strip(),
    }


def _login_response(conn: Connection, emp_id: int, employee_no: str, display_name: str, auth_s: str) -> dict:
    tokens = _issue_tokens(conn, emp_id, employee_no)
    return {
        "ok": True,
        **tokens,
        "employee_no": employee_no,
        "name": display_name,
        "auth_status": auth_s,
    }


@router.post("/login")
def mobile_login(body: LoginBody, conn: Connection = Depends(get_db)) -> dict:
    """비밀번호 미설정 시 최초 1회: 이름 일치하면 입력 비밀번호를 DB에 저장 후 토큰 발급. 이후는 사번·비밀번호만."""
    no = body.employee_no.strip()
    cur = conn.cursor(DictCursor)
    cur.execute(
        """
        SELECT id, employee_no, name, password_hash, auth_status
        FROM employees
        WHERE employee_no = %s
        LIMIT 1
        """,
        (no,),
    )
    row = cur.fetchone()
    msg_bad = "사번 또는 비밀번호가 올바르지 않습니다."
    if not row:
        raise HTTPException(status_code=401, detail=msg_bad)

    ph = row.get("password_hash")
    emp_id = int(row["id"])
    display_name = (row.get("name") or "").strip()

    if not ph:
        name_in = (body.name or "").strip()
        if not name_in:
            raise HTTPException(status_code=400, detail="최초 로그인입니다. 이름을 입력하세요.")
        if display_name != name_in:
            raise HTTPException(status_code=400, detail="이름이 사원관리 등록 정보와 일치하지 않습니다.")
        pwd_hash = hash_password(body.password)
        cur2 = conn.cursor()
        cur2.execute(
            """
            UPDATE employees
            SET password_hash=%s, auth_status='O'
            WHERE id=%s AND (password_hash IS NULL OR password_hash='')
            """,
            (pwd_hash, emp_id),
        )
        conn.commit()
        if cur2.rowcount == 0:
            raise HTTPException(
                status_code=409,
                detail="비밀번호가 이미 설정되었습니다. 이름 입력 없이 비밀번호만으로 다시 로그인하세요.",
            )
        publish_employee_auth_changed(emp_id)
        return _login_response(conn, emp_id, row["employee_no"], display_name, "O")

    if not verify_password(body.password, ph):
        raise HTTPException(status_code=401, detail=msg_bad)

    raw_auth = row.get("auth_status")
    if isinstance(raw_auth, (bytes, bytearray)):
        raw_auth = raw_auth.decode("ascii", errors="ignore")
    auth_s = str(raw_auth).strip() if raw_auth is not None else "X"
    if auth_s not in ("O", "X"):
        auth_s = "X"

    return _login_response(conn, emp_id, row["employee_no"], display_name, auth_s)


@router.post("/refresh")
def refresh_access_token(body: RefreshBody, conn: Connection = Depends(get_db)) -> dict:
    token = body.refresh_token.strip()
    if not token:
        raise HTTPException(status_code=400, detail="리프레시 토큰이 필요합니다.")
    try:
        payload = decode_mobile_refresh_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="리프레시 토큰이 만료되었습니다.") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.") from None

    if payload.get("typ") != "mobile_refresh":
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")
    try:
        emp_id = int(payload.get("sub") or 0)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.") from None

    token_hash = _hash_refresh_token(token)
    cur = conn.cursor(DictCursor)
    cur.execute(
        """
        SELECT id, employee_id, revoked_at, expires_at
        FROM mobile_refresh_tokens
        WHERE token_hash=%s
        LIMIT 1
        """,
        (token_hash,),
    )
    row = cur.fetchone()
    if not row or int(row["employee_id"]) != emp_id:
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")
    if row.get("revoked_at") is not None:
        raise HTTPException(status_code=401, detail="이미 사용된 리프레시 토큰입니다.")
    exp_at = row.get("expires_at")
    if exp_at and hasattr(exp_at, "timestamp") and exp_at.timestamp() < _now_utc_naive().timestamp():
        raise HTTPException(status_code=401, detail="리프레시 토큰이 만료되었습니다.")

    cur.execute(
        """
        SELECT id, employee_no, name, auth_status
        FROM employees
        WHERE id = %s
        LIMIT 1
        """,
        (emp_id,),
    )
    emp = cur.fetchone()
    if not emp:
        raise HTTPException(status_code=401, detail="사원을 찾을 수 없습니다.")

    # Rotation: invalidate used refresh token and issue new pair.
    cur2 = conn.cursor()
    cur2.execute(
        """
        UPDATE mobile_refresh_tokens
        SET revoked_at=%s
        WHERE id=%s AND revoked_at IS NULL
        """,
        (_now_utc_naive(), int(row["id"])),
    )
    if cur2.rowcount == 0:
        conn.rollback()
        raise HTTPException(status_code=401, detail="이미 사용된 리프레시 토큰입니다.")
    conn.commit()

    tokens = _issue_tokens(conn, emp_id, str(emp["employee_no"]))
    return {
        "ok": True,
        **tokens,
        "employee_no": str(emp["employee_no"]),
        "name": str(emp.get("name") or ""),
        "auth_status": str(emp.get("auth_status") or "X"),
    }


@router.get("/me")
def auth_me(
    cred: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    conn: Connection = Depends(get_db),
) -> dict:
    """Bearer JWT로 현재 사원 정보 (토큰 유효성·만료 검증)."""
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
        """
        SELECT e.id, e.employee_no, e.name, e.hire_date, e.status, e.auth_status, d.name AS department_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE e.id = %s
        LIMIT 1
        """,
        (emp_id,),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="사원을 찾을 수 없습니다.")
    raw_auth = row.get("auth_status")
    if isinstance(raw_auth, (bytes, bytearray)):
        raw_auth = raw_auth.decode("ascii", errors="ignore")
    if str(raw_auth).strip() != "O":
        raise HTTPException(status_code=401, detail="인증이 해제되었습니다. 다시 로그인하세요.")
    return _serialize_me(row)
