from __future__ import annotations

import re
from typing import Optional

import mariadb
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.database import get_db

router = APIRouter(prefix="/leave-codes", tags=["leave-codes"])


class LeaveCodeCreate(BaseModel):
    name: str = Field(..., min_length=1)
    code: Optional[str] = None


class LeaveCodeUpdate(BaseModel):
    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


def _next_leave_code(conn: mariadb.Connection) -> str:
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT code FROM leave_codes")
    max_n = 0
    for row in cur.fetchall() or []:
        m = re.match(r"^V(\d+)$", row["code"], re.I)
        if m:
            max_n = max(max_n, int(m.group(1)))
    n = max_n + 1
    w = 3 if n >= 100 else 2
    return f"V{str(n).zfill(w)}"


@router.get("")
def list_leave_codes(conn: mariadb.Connection = Depends(get_db)) -> list[dict]:
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, code, name FROM leave_codes ORDER BY code")
    return list(cur.fetchall() or [])


@router.post("", status_code=201)
def create_leave_code(body: LeaveCodeCreate, conn: mariadb.Connection = Depends(get_db)) -> dict:
    name = body.name.strip()
    code = (body.code or "").strip() or _next_leave_code(conn)
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO leave_codes (code, name) VALUES (%s, %s)", (code, name))
        conn.commit()
        new_id = cur.lastrowid
    except mariadb.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=409, detail=str(e)) from e
    return {"id": int(new_id), "code": code, "name": name}


@router.put("/{leave_id}")
def update_leave_code(
    leave_id: int, body: LeaveCodeUpdate, conn: mariadb.Connection = Depends(get_db)
) -> dict:
    cur = conn.cursor()
    cur.execute(
        "UPDATE leave_codes SET code=%s, name=%s WHERE id=%s",
        (body.code.strip(), body.name.strip(), leave_id),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


@router.delete("/{leave_id}", status_code=204)
def delete_leave_code(leave_id: int, conn: mariadb.Connection = Depends(get_db)) -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM leave_codes WHERE id=%s", (leave_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
