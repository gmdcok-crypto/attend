from __future__ import annotations

import re
from datetime import datetime, time, timedelta
from typing import Union

import mariadb
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.database import get_db

router = APIRouter(prefix="/work-shifts", tags=["work-shifts"])


class WorkShiftCreate(BaseModel):
    name: str = Field(..., min_length=1)
    clock_in: str = Field(..., min_length=1, description="HH:MM 또는 HH:MM:SS")
    clock_out: str = Field(..., min_length=1)


class WorkShiftUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    clock_in: str = Field(..., min_length=1)
    clock_out: str = Field(..., min_length=1)


def _parse_hhmm(s: str) -> time:
    s = s.strip()
    m = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", s)
    if not m:
        raise ValueError("invalid time")
    h, mi, sec = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    if not (0 <= h <= 23 and 0 <= mi <= 59 and 0 <= sec <= 59):
        raise ValueError("invalid time")
    return time(h, mi, sec)


def _time_to_str(v: Union[time, timedelta, datetime, str, None]) -> str:
    if v is None:
        return "00:00"
    if isinstance(v, time):
        return v.strftime("%H:%M")
    if isinstance(v, timedelta):
        secs = int(v.total_seconds()) % 86400
        if secs < 0:
            secs += 86400
        h, r = divmod(secs, 3600)
        m, _ = divmod(r, 60)
        return f"{h:02d}:{m:02d}"
    if isinstance(v, datetime):
        return v.strftime("%H:%M")
    s = str(v)
    return s[:5] if len(s) >= 5 else s


def _serialize(row: dict) -> dict:
    return {
        "id": int(row["id"]),
        "name": row["name"],
        "clock_in": _time_to_str(row["clock_in"]),
        "clock_out": _time_to_str(row["clock_out"]),
        "sort_order": int(row.get("sort_order") or 0),
    }


@router.get("")
def list_work_shifts(conn: mariadb.Connection = Depends(get_db)) -> list[dict]:
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT id, name, clock_in, clock_out, sort_order
        FROM work_shift_types
        ORDER BY sort_order ASC, id ASC
        """
    )
    return [_serialize(r) for r in (cur.fetchall() or [])]


@router.post("", status_code=201)
def create_work_shift(body: WorkShiftCreate, conn: mariadb.Connection = Depends(get_db)) -> dict:
    name = body.name.strip()
    try:
        tin = _parse_hhmm(body.clock_in)
        tout = _parse_hhmm(body.clock_out)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="출근·퇴근 시각 형식은 HH:MM 입니다.") from e
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 AS n FROM work_shift_types")
    row = cur.fetchone()
    next_sort = int(row["n"]) if row else 1
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO work_shift_types (name, clock_in, clock_out, sort_order)
        VALUES (%s, %s, %s, %s)
        """,
        (name, tin, tout, next_sort),
    )
    conn.commit()
    return {"id": int(cur.lastrowid)}


@router.put("/{shift_id}")
def update_work_shift(
    shift_id: int, body: WorkShiftUpdate, conn: mariadb.Connection = Depends(get_db)
) -> dict:
    name = body.name.strip()
    try:
        tin = _parse_hhmm(body.clock_in)
        tout = _parse_hhmm(body.clock_out)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="출근·퇴근 시각 형식은 HH:MM 입니다.") from e
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE work_shift_types
        SET name=%s, clock_in=%s, clock_out=%s
        WHERE id=%s
        """,
        (name, tin, tout, shift_id),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


@router.delete("/{shift_id}", status_code=204)
def delete_work_shift(shift_id: int, conn: mariadb.Connection = Depends(get_db)) -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM work_shift_types WHERE id=%s", (shift_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
