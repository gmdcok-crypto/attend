from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.database import Connection, DictCursor, get_db

router = APIRouter(prefix="/attendance-events", tags=["attendance"])


@router.get("")
def list_attendance_events(
    conn: Connection = Depends(get_db),
    date_from: str = Query(..., description="YYYY-MM-DD"),
    date_to: str = Query(..., description="YYYY-MM-DD"),
    employee_id: Optional[int] = Query(None),
    employee_name: Optional[str] = Query(None),
) -> list[dict]:
    cur = conn.cursor(DictCursor)
    cur.execute("SET time_zone = '+09:00'")
    name_like = f"%{employee_name.strip()}%" if employee_name and employee_name.strip() else None

    if employee_id is not None:
        cur.execute(
            """
            SELECT a.id, a.event_type, a.occurred_at, e.employee_no, e.name AS employee_name
            FROM attendance_events a
            INNER JOIN employees e ON e.id = a.employee_id
            WHERE DATE(a.occurred_at) BETWEEN %s AND %s
              AND a.employee_id = %s
            ORDER BY a.occurred_at DESC
            """,
            (date_from, date_to, employee_id),
        )
    elif name_like:
        cur.execute(
            """
            SELECT a.id, a.event_type, a.occurred_at, e.employee_no, e.name AS employee_name
            FROM attendance_events a
            INNER JOIN employees e ON e.id = a.employee_id
            WHERE DATE(a.occurred_at) BETWEEN %s AND %s
              AND e.name LIKE %s
            ORDER BY a.occurred_at DESC
            """,
            (date_from, date_to, name_like),
        )
    else:
        cur.execute(
            """
            SELECT a.id, a.event_type, a.occurred_at, e.employee_no, e.name AS employee_name
            FROM attendance_events a
            INNER JOIN employees e ON e.id = a.employee_id
            WHERE DATE(a.occurred_at) BETWEEN %s AND %s
            ORDER BY a.occurred_at DESC
            """,
            (date_from, date_to),
        )

    rows = cur.fetchall() or []
    out: list[dict] = []
    for r in rows:
        oc = r["occurred_at"]
        if isinstance(oc, datetime):
            oc_iso = oc.isoformat()
        else:
            oc_iso = str(oc)
        out.append(
            {
                "id": int(r["id"]),
                "event_type": r["event_type"],
                "occurred_at": oc_iso,
                "employee_no": r["employee_no"],
                "employee_name": r["employee_name"],
            }
        )
    return out
