"""모바일 — 연차촉진 PIN·열람·전자서명."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from backend.database import Connection, DictCursor, get_db
from backend.deps_mobile import get_mobile_employee_id
from backend.passwords import hash_password, verify_password

pin_router = APIRouter(prefix="/mobile/pin", tags=["mobile-pin"])
lp_router = APIRouter(prefix="/mobile/leave-promotion", tags=["mobile-leave-promotion"])


def _validate_pin(pin: str) -> None:
    if not re.fullmatch(r"\d{6}", pin or ""):
        raise HTTPException(status_code=400, detail="PIN은 6자리 숫자여야 합니다.")


class PinBody(BaseModel):
    pin: str = Field(..., min_length=6, max_length=6)


@pin_router.get("/status")
def pin_status(
    employee_id: int = Depends(get_mobile_employee_id),
    conn: Connection = Depends(get_db),
) -> dict:
    cur = conn.cursor(DictCursor)
    cur.execute("SELECT pin_hash FROM employees WHERE id = %s", (employee_id,))
    row = cur.fetchone()
    ph = row.get("pin_hash") if row else None
    has_pin = bool(ph and str(ph).strip())
    return {"has_pin": has_pin}


@pin_router.post("/setup")
def pin_setup(
    body: PinBody,
    employee_id: int = Depends(get_mobile_employee_id),
    conn: Connection = Depends(get_db),
) -> dict:
    _validate_pin(body.pin)
    h = hash_password(body.pin)
    cur = conn.cursor()
    cur.execute("UPDATE employees SET pin_hash = %s WHERE id = %s", (h, employee_id))
    conn.commit()
    return {"ok": True}


@pin_router.post("/verify")
def pin_verify(
    body: PinBody,
    employee_id: int = Depends(get_mobile_employee_id),
    conn: Connection = Depends(get_db),
) -> dict:
    _validate_pin(body.pin)
    cur = conn.cursor(DictCursor)
    cur.execute("SELECT pin_hash FROM employees WHERE id = %s", (employee_id,))
    row = cur.fetchone()
    if not row or not row.get("pin_hash"):
        raise HTTPException(status_code=400, detail="PIN이 설정되어 있지 않습니다.")
    if not verify_password(body.pin, str(row["pin_hash"])):
        raise HTTPException(status_code=400, detail="PIN이 일치하지 않습니다.")
    return {"ok": True}


def _iso(v: object) -> str | None:
    if v is None:
        return None
    if hasattr(v, "isoformat"):
        return v.isoformat()  # type: ignore[no-any-return]
    return str(v)


@lp_router.get("/current")
def get_current(
    employee_id: int = Depends(get_mobile_employee_id),
    conn: Connection = Depends(get_db),
) -> dict:
    cur = conn.cursor(DictCursor)
    cur.execute("SELECT pin_hash FROM employees WHERE id = %s", (employee_id,))
    row = cur.fetchone()
    has_pin = bool(row and row.get("pin_hash") and str(row["pin_hash"]).strip())

    cur.execute(
        """
        SELECT c.id, c.title, c.doc_version, c.message_text, c.doc_hash,
               t.read_at, t.signed_at
        FROM leave_promotion_targets t
        INNER JOIN leave_promotion_campaigns c ON c.id = t.campaign_id
        WHERE t.employee_id = %s
        ORDER BY c.id DESC
        LIMIT 1
        """,
        (employee_id,),
    )
    r = cur.fetchone()
    if not r:
        return {"has_pin": has_pin, "campaign": None}

    return {
        "has_pin": has_pin,
        "campaign": {
            "id": int(r["id"]),
            "title": r["title"],
            "doc_version": r["doc_version"],
            "message": r["message_text"],
            "doc_hash": r["doc_hash"],
            "read_at": _iso(r.get("read_at")),
            "signed_at": _iso(r.get("signed_at")),
        },
    }


@lp_router.post("/{campaign_id}/read")
def mark_read(
    campaign_id: int,
    employee_id: int = Depends(get_mobile_employee_id),
    conn: Connection = Depends(get_db),
) -> dict:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE leave_promotion_targets
        SET read_at = COALESCE(read_at, CURRENT_TIMESTAMP(3))
        WHERE campaign_id = %s AND employee_id = %s
        """,
        (campaign_id, employee_id),
    )
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="대상 캠페인이 없습니다.")
    conn.commit()
    return {"ok": True}


class SignBody(BaseModel):
    pin: str = Field(..., min_length=6, max_length=6)


@lp_router.post("/{campaign_id}/sign")
def sign(
    campaign_id: int,
    body: SignBody,
    request: Request,
    employee_id: int = Depends(get_mobile_employee_id),
    conn: Connection = Depends(get_db),
) -> dict:
    _validate_pin(body.pin)
    cur = conn.cursor(DictCursor)
    cur.execute("SELECT pin_hash FROM employees WHERE id = %s", (employee_id,))
    row = cur.fetchone()
    if not row or not row.get("pin_hash"):
        raise HTTPException(status_code=400, detail="먼저 모바일에서 PIN을 설정하세요.")
    if not verify_password(body.pin, str(row["pin_hash"])):
        raise HTTPException(status_code=400, detail="PIN이 일치하지 않습니다.")

    cur.execute(
        """
        SELECT c.doc_hash AS doc_hash, t.signed_at AS signed_at
        FROM leave_promotion_targets t
        JOIN leave_promotion_campaigns c ON c.id = t.campaign_id
        WHERE t.campaign_id = %s AND t.employee_id = %s
        LIMIT 1
        """,
        (campaign_id, employee_id),
    )
    r = cur.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="대상 캠페인이 없습니다.")
    if r.get("signed_at"):
        raise HTTPException(status_code=400, detail="이미 서명이 완료되었습니다.")

    doc_hash = str(r["doc_hash"])
    client_ip = request.client.host if request.client else None
    ua = (request.headers.get("user-agent") or "")[:512]

    cur2 = conn.cursor()
    cur2.execute(
        """
        INSERT INTO leave_promotion_signatures (campaign_id, employee_id, doc_hash, client_ip, user_agent)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (campaign_id, employee_id, doc_hash, client_ip, ua),
    )
    cur2.execute(
        """
        UPDATE leave_promotion_targets
        SET signed_at = CURRENT_TIMESTAMP(3)
        WHERE campaign_id = %s AND employee_id = %s AND signed_at IS NULL
        """,
        (campaign_id, employee_id),
    )
    conn.commit()
    return {"ok": True, "doc_hash": doc_hash}
