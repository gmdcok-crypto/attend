"""모바일 — 연차(휴가) 사용 계획 등록·조회."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.database import Connection, DictCursor, get_db
from backend.deps_mobile import get_mobile_employee_id

router = APIRouter(prefix="/mobile/leave-plans", tags=["mobile-leave-plans"])

LeaveUnit = Literal["FULL", "AM", "PM"]


class LeavePlanCreate(BaseModel):
    leave_code_id: int = Field(..., ge=1)
    date_from: str = Field(..., min_length=10, description="YYYY-MM-DD")
    date_to: str = Field(..., min_length=10, description="YYYY-MM-DD")
    leave_unit: LeaveUnit = "FULL"
    reason: str = Field(default="", max_length=500)


def _parse_date(s: str) -> date:
    return date.fromisoformat(s.strip()[:10])


@router.get("")
def list_my_leave_plans(
    employee_id: int = Depends(get_mobile_employee_id),
    conn: Connection = Depends(get_db),
) -> list[dict]:
    cur = conn.cursor(DictCursor)
    cur.execute(
        """
        SELECT p.id, p.leave_code_id, p.date_from, p.date_to, p.leave_unit, p.reason, p.status,
               p.created_at, lc.name AS leave_name
        FROM leave_plan_requests p
        JOIN leave_codes lc ON lc.id = p.leave_code_id
        WHERE p.employee_id = %s
        ORDER BY p.date_from DESC, p.id DESC
        """,
        (employee_id,),
    )
    rows = cur.fetchall() or []
    out: list[dict] = []
    for r in rows:
        df = r["date_from"]
        dt = r["date_to"]
        out.append(
            {
                "id": int(r["id"]),
                "leave_code_id": int(r["leave_code_id"]),
                "leave_name": r["leave_name"],
                "date_from": df.isoformat() if hasattr(df, "isoformat") else str(df)[:10],
                "date_to": dt.isoformat() if hasattr(dt, "isoformat") else str(dt)[:10],
                "leave_unit": r["leave_unit"],
                "reason": r.get("reason") or "",
                "status": r["status"],
                "created_at": str(r["created_at"]) if r.get("created_at") is not None else None,
            }
        )
    return out


@router.post("", status_code=201)
def create_leave_plan(
    body: LeavePlanCreate,
    employee_id: int = Depends(get_mobile_employee_id),
    conn: Connection = Depends(get_db),
) -> dict:
    try:
        df = _parse_date(body.date_from)
        dt = _parse_date(body.date_to)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다.") from e
    if dt < df:
        raise HTTPException(status_code=400, detail="종료일은 시작일 이후여야 합니다.")
    cur = conn.cursor(DictCursor)
    cur.execute("SELECT id FROM leave_codes WHERE id = %s LIMIT 1", (body.leave_code_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=400, detail="휴가 종류를 찾을 수 없습니다.")
    reason = (body.reason or "").strip()
    ins = conn.cursor()
    ins.execute(
        """
        INSERT INTO leave_plan_requests
          (employee_id, leave_code_id, date_from, date_to, leave_unit, reason, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'PLANNED')
        """,
        (employee_id, body.leave_code_id, df, dt, body.leave_unit, reason or None),
    )
    conn.commit()
    return {"id": int(ins.lastrowid)}
