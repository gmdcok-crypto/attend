from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.database import Connection, DictCursor, get_db

router = APIRouter(prefix="/attendance-events", tags=["attendance"])


class AttendanceEventWrite(BaseModel):
    employee_no: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1, description="IN|OUT 또는 출근|퇴근")
    event_date: str = Field(..., min_length=1, description="YYYY-MM-DD")
    event_time: str = Field(..., min_length=1, description="HH:MM 또는 HH:MM:SS")


def _resolve_employee_id(conn: Connection, employee_no: str) -> int:
    cur = conn.cursor(DictCursor)
    cur.execute(
        "SELECT id FROM employees WHERE employee_no = %s LIMIT 1",
        (employee_no.strip(),),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="사번에 해당하는 사원을 찾을 수 없습니다.")
    return int(row["id"])


def _normalize_event_type(v: str) -> str:
    s = v.strip().upper()
    if s in ("IN", "출근"):
        return "IN"
    if s in ("OUT", "퇴근"):
        return "OUT"
    raise HTTPException(status_code=400, detail="구분은 IN/OUT(또는 출근/퇴근)만 허용됩니다.")


def _parse_occurred_at(event_date: str, event_time: str) -> datetime:
    try:
        d = date.fromisoformat(event_date.strip()[:10])
    except ValueError as e:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)") from e

    t_raw = event_time.strip()
    fmt = "%H:%M:%S" if len(t_raw) >= 8 else "%H:%M"
    try:
        t = datetime.strptime(t_raw[:8], fmt).time()
    except ValueError as e:
        raise HTTPException(status_code=400, detail="시간 형식이 올바르지 않습니다. (HH:MM 또는 HH:MM:SS)") from e
    if isinstance(t, time):
        return datetime.combine(d, t)
    raise HTTPException(status_code=400, detail="시간 형식이 올바르지 않습니다.")


def _enforce_daily_single_event(
    conn: Connection, employee_id: int, event_type: str, occurred_at: datetime, exclude_id: int | None = None
) -> None:
    cur = conn.cursor(DictCursor)
    q = """
        SELECT id
        FROM attendance_events
        WHERE employee_id = %s
          AND event_type = %s
          AND DATE(occurred_at) = DATE(%s)
    """
    params: list[object] = [employee_id, event_type, occurred_at]
    if exclude_id is not None:
        q += " AND id <> %s"
        params.append(exclude_id)
    q += " LIMIT 1"
    cur.execute(q, tuple(params))
    if cur.fetchone():
        label = "출근" if event_type == "IN" else "퇴근"
        raise HTTPException(status_code=409, detail=f"해당 날짜의 {label} 기록은 1회만 가능합니다.")


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


@router.post("", status_code=201)
def create_attendance_event(body: AttendanceEventWrite, conn: Connection = Depends(get_db)) -> dict:
    employee_id = _resolve_employee_id(conn, body.employee_no)
    event_type = _normalize_event_type(body.event_type)
    occurred_at = _parse_occurred_at(body.event_date, body.event_time)
    _enforce_daily_single_event(conn, employee_id, event_type, occurred_at)

    cur = conn.cursor()
    cur.execute("SET time_zone = '+09:00'")
    cur.execute(
        """
        INSERT INTO attendance_events (employee_id, event_type, occurred_at, source, device_info)
        VALUES (%s, %s, %s, 'MANUAL', 'admin-raw-edit')
        """,
        (employee_id, event_type, occurred_at),
    )
    conn.commit()
    return {"id": int(cur.lastrowid)}


@router.put("/{event_id}")
def update_attendance_event(
    event_id: int, body: AttendanceEventWrite, conn: Connection = Depends(get_db)
) -> dict:
    employee_id = _resolve_employee_id(conn, body.employee_no)
    event_type = _normalize_event_type(body.event_type)
    occurred_at = _parse_occurred_at(body.event_date, body.event_time)
    _enforce_daily_single_event(conn, employee_id, event_type, occurred_at, exclude_id=event_id)

    cur = conn.cursor()
    cur.execute("SET time_zone = '+09:00'")
    cur.execute(
        """
        UPDATE attendance_events
        SET employee_id=%s, event_type=%s, occurred_at=%s, source='MANUAL', device_info='admin-raw-edit'
        WHERE id=%s
        """,
        (employee_id, event_type, occurred_at, event_id),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="해당 원시자료를 찾을 수 없습니다.")
    return {"ok": True}


@router.delete("/{event_id}", status_code=204)
def delete_attendance_event(event_id: int, conn: Connection = Depends(get_db)) -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM attendance_events WHERE id=%s", (event_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="해당 원시자료를 찾을 수 없습니다.")
