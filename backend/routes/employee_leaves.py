from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.database import Connection, DictCursor, get_db
from backend.deps_mobile import get_mobile_employee_id

router = APIRouter(prefix="/employee-leaves", tags=["employee-leaves"])


class EmployeeLeaveCreate(BaseModel):
    employee_no: str = Field(..., min_length=1)
    leave_code_id: int = Field(..., ge=1)
    start_date: str = Field(..., min_length=1)
    end_date: str = Field(..., min_length=1)


class EmployeeLeaveUpdate(BaseModel):
    employee_no: str = Field(..., min_length=1)
    leave_code_id: int = Field(..., ge=1)
    start_date: str = Field(..., min_length=1)
    end_date: str = Field(..., min_length=1)


def _parse_date(s: str) -> date:
    return date.fromisoformat(s[:10])


def _calendar_days(a: date, b: date) -> int:
    return (b - a).days + 1


def _workdays(a: date, b: date) -> int:
    n = 0
    d = a
    while d <= b:
        if d.weekday() < 5:
            n += 1
        d += timedelta(days=1)
    return n


def _resolve_employee_id(conn: Connection, employee_no: str) -> Optional[int]:
    cur = conn.cursor(DictCursor)
    cur.execute(
        "SELECT id FROM employees WHERE employee_no = %s LIMIT 1",
        (employee_no.strip(),),
    )
    row = cur.fetchone()
    return int(row["id"]) if row else None


def _load_all_records_for_aggregate(
    conn: Connection, employee_ids: list[int]
) -> list[dict]:
    if not employee_ids:
        return []
    cur = conn.cursor(DictCursor)
    placeholders = ",".join(["%s"] * len(employee_ids))
    cur.execute(
        f"""
        SELECT employee_id, leave_code_id, start_date, end_date
        FROM employee_leave_records
        WHERE employee_id IN ({placeholders})
        """,
        tuple(employee_ids),
    )
    return list(cur.fetchall() or [])


def _as_date(v: object) -> date:
    if isinstance(v, date):
        return v
    return date.fromisoformat(str(v)[:10])


def _aggregate_workdays_by_year(rows: list[dict]) -> dict[tuple[int, int, int], float]:
    out: dict[tuple[int, int, int], float] = {}
    for r in rows:
        emp_id = int(r["employee_id"])
        lc_id = int(r["leave_code_id"])
        sd = _as_date(r["start_date"])
        ed = _as_date(r["end_date"])
        y = sd.year
        key = (emp_id, lc_id, y)
        out[key] = out.get(key, 0.0) + float(_workdays(sd, ed))
    return out


def _load_quotas(conn: Connection) -> dict[tuple[int, int, int], float]:
    cur = conn.cursor(DictCursor)
    cur.execute(
        "SELECT employee_id, leave_code_id, year_year, quota_days FROM employee_leave_quotas"
    )
    q: dict[tuple[int, int, int], float] = {}
    for r in cur.fetchall() or []:
        key = (int(r["employee_id"]), int(r["leave_code_id"]), int(r["year_year"]))
        q[key] = float(r["quota_days"])
    return q


def _serialize_row(
    r: dict,
    agg: dict[tuple[int, int, int], float],
    quotas: dict[tuple[int, int, int], float],
) -> dict:
    sd = _as_date(r["start_date"])
    ed = _as_date(r["end_date"])
    emp_id = int(r["employee_id"])
    lc_id = int(r["leave_code_id"])
    y = sd.year
    key = (emp_id, lc_id, y)
    total_cal = _calendar_days(sd, ed)
    wd = _workdays(sd, ed)
    cumul = agg.get(key, 0.0)
    qv = quotas.get(key)
    remaining: Optional[float] = None
    if qv is not None:
        remaining = round(qv - cumul, 1)
    return {
        "id": int(r["id"]),
        "employee_id": emp_id,
        "employee_no": r["employee_no"],
        "name": r["name"],
        "leave_code_id": lc_id,
        "leave_code": r["leave_code"],
        "leave_name": r["leave_name"],
        "start_date": sd.isoformat(),
        "end_date": ed.isoformat(),
        "total_days": total_cal,
        "work_days": wd,
        "cumulative_work_days": round(cumul, 1),
        "remaining_days": remaining,
    }


@router.get("")
def list_employee_leaves(
    conn: Connection = Depends(get_db),
    date_from: Optional[str] = Query(None, alias="date_from"),
    date_to: Optional[str] = Query(None, alias="date_to"),
    q: Optional[str] = Query(None, description="사번·성명 부분 검색"),
) -> list[dict]:
    cur = conn.cursor(DictCursor)
    clauses: list[str] = ["1=1"]
    params: list[object] = []

    if date_from and date_to:
        try:
            df = _parse_date(date_from)
            dt = _parse_date(date_to)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="기간 날짜 형식이 올바르지 않습니다.") from e
        if dt < df:
            df, dt = dt, df
        clauses.append("r.start_date <= %s AND r.end_date >= %s")
        params.extend([dt, df])

    if q and q.strip():
        like = f"%{q.strip()}%"
        clauses.append("(e.employee_no LIKE %s OR e.name LIKE %s)")
        params.extend([like, like])

    where_sql = " AND ".join(clauses)
    cur.execute(
        f"""
        SELECT r.id, r.employee_id, r.leave_code_id, r.start_date, r.end_date,
               e.employee_no, e.name, lc.code AS leave_code, lc.name AS leave_name
        FROM employee_leave_records r
        JOIN employees e ON e.id = r.employee_id
        JOIN leave_codes lc ON lc.id = r.leave_code_id
        WHERE {where_sql}
        ORDER BY r.start_date DESC, e.employee_no, r.id
        """,
        tuple(params),
    )
    raw_rows = list(cur.fetchall() or [])
    emp_ids = list({int(r["employee_id"]) for r in raw_rows})
    all_for_agg = _load_all_records_for_aggregate(conn, emp_ids)
    agg = _aggregate_workdays_by_year(all_for_agg)
    quotas = _load_quotas(conn)
    return [_serialize_row(r, agg, quotas) for r in raw_rows]


@router.get("/me/summary")
def my_leave_summary(
    employee_id: int = Depends(get_mobile_employee_id),
    year: Optional[int] = Query(None, description="기준 연도(기본: 올해)"),
    conn: Connection = Depends(get_db),
) -> dict:
    """모바일: 본인 연도별 휴가 배정·사용·잔여 요약."""
    today = date.today()
    y = year if year is not None else today.year
    cur = conn.cursor(DictCursor)
    cur.execute(
        """
        SELECT lc.id AS leave_code_id, lc.code AS leave_code, lc.name AS leave_name,
               q.quota_days
        FROM employee_leave_quotas q
        JOIN leave_codes lc ON lc.id = q.leave_code_id
        WHERE q.employee_id = %s AND q.year_year = %s
        ORDER BY lc.code
        """,
        (employee_id, y),
    )
    quota_rows = list(cur.fetchall() or [])
    all_for_agg = _load_all_records_for_aggregate(conn, [employee_id])
    agg = _aggregate_workdays_by_year(all_for_agg)
    items: list[dict] = []
    for r in quota_rows:
        lc_id = int(r["leave_code_id"])
        key = (employee_id, lc_id, y)
        used = round(float(agg.get(key, 0.0)), 1)
        qv = float(r["quota_days"])
        items.append(
            {
                "leave_code_id": lc_id,
                "leave_code": r["leave_code"],
                "leave_name": r["leave_name"],
                "quota_days": qv,
                "used_days": used,
                "remaining_days": round(qv - used, 1),
            }
        )
    return {"year": y, "items": items}


@router.get("/me")
def list_my_employee_leaves(
    employee_id: int = Depends(get_mobile_employee_id),
    year: Optional[int] = Query(None, description="조회 연도(기본: 올해, 해당 연도와 겹치는 기록)"),
    conn: Connection = Depends(get_db),
) -> list[dict]:
    """모바일: 본인 휴가(연차 등) 사용 기록."""
    today = date.today()
    y = year if year is not None else today.year
    df = date(y, 1, 1)
    dt = date(y, 12, 31)
    cur = conn.cursor(DictCursor)
    cur.execute(
        """
        SELECT r.id, r.employee_id, r.leave_code_id, r.start_date, r.end_date,
               e.employee_no, e.name, lc.code AS leave_code, lc.name AS leave_name
        FROM employee_leave_records r
        JOIN employees e ON e.id = r.employee_id
        JOIN leave_codes lc ON lc.id = r.leave_code_id
        WHERE e.id = %s AND r.start_date <= %s AND r.end_date >= %s
        ORDER BY r.start_date DESC, r.id DESC
        """,
        (employee_id, dt, df),
    )
    raw_rows = list(cur.fetchall() or [])
    all_for_agg = _load_all_records_for_aggregate(conn, [employee_id])
    agg = _aggregate_workdays_by_year(all_for_agg)
    quotas = _load_quotas(conn)
    return [_serialize_row(r, agg, quotas) for r in raw_rows]


@router.post("", status_code=201)
def create_employee_leave(body: EmployeeLeaveCreate, conn: Connection = Depends(get_db)) -> dict:
    emp_id = _resolve_employee_id(conn, body.employee_no)
    if emp_id is None:
        raise HTTPException(status_code=400, detail="해당 사번의 사원을 찾을 수 없습니다.")
    try:
        sd = _parse_date(body.start_date)
        ed = _parse_date(body.end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다.") from e
    if ed < sd:
        raise HTTPException(status_code=400, detail="휴가 종료일은 시작일 이후여야 합니다.")
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO employee_leave_records (employee_id, leave_code_id, start_date, end_date)
        VALUES (%s, %s, %s, %s)
        """,
        (emp_id, body.leave_code_id, sd, ed),
    )
    conn.commit()
    return {"id": int(cur.lastrowid)}


@router.put("/{record_id}")
def update_employee_leave(
    record_id: int, body: EmployeeLeaveUpdate, conn: Connection = Depends(get_db)
) -> dict:
    emp_id = _resolve_employee_id(conn, body.employee_no)
    if emp_id is None:
        raise HTTPException(status_code=400, detail="해당 사번의 사원을 찾을 수 없습니다.")
    try:
        sd = _parse_date(body.start_date)
        ed = _parse_date(body.end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다.") from e
    if ed < sd:
        raise HTTPException(status_code=400, detail="휴가 종료일은 시작일 이후여야 합니다.")
    cur = conn.cursor(DictCursor)
    cur.execute(
        "SELECT id FROM employee_leave_records WHERE id = %s LIMIT 1",
        (record_id,),
    )
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="해당 휴가 기록을 찾을 수 없습니다.")
    cur.execute(
        """
        UPDATE employee_leave_records
        SET employee_id=%s, leave_code_id=%s, start_date=%s, end_date=%s
        WHERE id=%s
        """,
        (emp_id, body.leave_code_id, sd, ed, record_id),
    )
    conn.commit()
    # MySQL 은 값이 동일하면 변경 행 수를 0으로 돌려줄 수 있어 rowcount 로 404 를 내지 않는다.
    return {"ok": True}


@router.delete("/{record_id}", status_code=204)
def delete_employee_leave(record_id: int, conn: Connection = Depends(get_db)) -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM employee_leave_records WHERE id=%s", (record_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
