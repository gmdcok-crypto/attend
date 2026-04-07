from __future__ import annotations

import calendar
import os
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


def _ref_date_for_leave_year(y: int) -> date:
    """연차 기준일: 당해 연도는 오늘, 과거 연도는 그 해 말일."""
    today = date.today()
    if y == today.year:
        return today
    return date(y, 12, 31)


def _anniversary_in_year(hire: date, year: int) -> date:
    """입사일의 기념일(윤일 29일 → 평년 28일 등 보정)."""
    last = calendar.monthrange(year, hire.month)[1]
    day = min(hire.day, last)
    return date(year, hire.month, day)


def base_annual_leave_days_kr(hire: date, ref: date) -> float:
    """관리자 화면 기준연차(입사일 기준) — 클라 calcBaseAnnualLeaveByHireDate 와 동일 규칙."""
    if hire > ref:
        return 0.0
    ann = _anniversary_in_year(hire, ref.year)
    if ref < ann:
        years = ref.year - hire.year - 1
    else:
        years = ref.year - hire.year
    if years < 1:
        months = (ref.year - hire.year) * 12 + (ref.month - hire.month)
        if ref.day < hire.day:
            months -= 1
        return float(max(0, min(11, months)))
    extra = max(0, (years - 1) // 2)
    return float(min(25, 15 + extra))


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


def _resolve_annual_leave_code_id(conn: Connection) -> int:
    """환경변수 ANNUAL_LEAVE_CODE(기본 V01)에 해당하는 휴가코드 id."""
    code = (os.getenv("ANNUAL_LEAVE_CODE") or "V01").strip()
    cur = conn.cursor(DictCursor)
    cur.execute("SELECT id FROM leave_codes WHERE code = %s LIMIT 1", (code,))
    row = cur.fetchone()
    if row:
        return int(row["id"])
    cur.execute("SELECT id FROM leave_codes ORDER BY code LIMIT 1")
    row = cur.fetchone()
    if not row:
        raise HTTPException(
            status_code=500, detail="휴가 코드가 등록되어 있지 않습니다."
        )
    return int(row["id"])


def _annual_line_payload(conn: Connection, employee_id: int, y: int) -> dict:
    """연차(지정 휴가코드) 1줄: 기준·기록·사용·잔여 (입사일 기준 산정, DB 한도표 없음)."""
    cur = conn.cursor(DictCursor)
    cur.execute(
        "SELECT hire_date FROM employees WHERE id = %s LIMIT 1", (employee_id,)
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="사원을 찾을 수 없습니다.")
    hire = _as_date(row["hire_date"])
    ref = _ref_date_for_leave_year(y)
    base = round(base_annual_leave_days_kr(hire, ref), 1)
    lc_id = _resolve_annual_leave_code_id(conn)
    cur.execute(
        "SELECT code, name FROM leave_codes WHERE id = %s LIMIT 1", (lc_id,)
    )
    lc_row = cur.fetchone()
    if not lc_row:
        raise HTTPException(
            status_code=500, detail="연차 휴가 코드를 찾을 수 없습니다."
        )
    all_for_agg = _load_all_records_for_aggregate(conn, [employee_id])
    agg = _aggregate_workdays_by_year(all_for_agg)
    key = (employee_id, lc_id, y)
    used_records = round(float(agg.get(key, 0.0)), 1)
    quota_days = float(base)
    initial = 0.0
    used_total = round(initial + used_records, 1)
    remaining = round(quota_days - used_total, 1)
    return {
        "year": y,
        "leave_code_id": lc_id,
        "leave_code": lc_row["code"],
        "leave_name": lc_row["name"],
        "base_days": base,
        "quota_days": round(quota_days, 1),
        "used_from_records_days": used_records,
        "initial_used_days": initial,
        "used_days": used_total,
        "remaining_days": remaining,
    }


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


def _serialize_row(
    r: dict,
    agg: dict[tuple[int, int, int], float],
    annual_lc_id: int,
    hire_by_emp: dict[int, date],
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
    remaining: Optional[float] = None
    hire = hire_by_emp.get(emp_id)
    if hire is not None and lc_id == annual_lc_id:
        ref = _ref_date_for_leave_year(y)
        base = round(base_annual_leave_days_kr(hire, ref), 1)
        remaining = round(base - cumul, 1)
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
        "initial_used_days": 0.0,
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
    annual_lc_id = _resolve_annual_leave_code_id(conn)
    hire_by_emp: dict[int, date] = {}
    if emp_ids:
        ph = ",".join(["%s"] * len(emp_ids))
        cur.execute(
            f"SELECT id, hire_date FROM employees WHERE id IN ({ph})",
            tuple(emp_ids),
        )
        for hr in cur.fetchall() or []:
            hire_by_emp[int(hr["id"])] = _as_date(hr["hire_date"])
    return [_serialize_row(r, agg, annual_lc_id, hire_by_emp) for r in raw_rows]


def _leave_summary_payload(conn: Connection, employee_id: int, y: int) -> dict:
    """연도별 휴가 사용·잔여 (코드별). 연차는 입사일 기준 산정, 한도 DB 없음."""
    cur = conn.cursor(DictCursor)
    cur.execute(
        "SELECT hire_date FROM employees WHERE id = %s LIMIT 1",
        (employee_id,),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="사원을 찾을 수 없습니다.")
    hire = _as_date(row["hire_date"])
    ref = _ref_date_for_leave_year(y)
    annual_lc_id = _resolve_annual_leave_code_id(conn)
    all_for_agg = _load_all_records_for_aggregate(conn, [employee_id])
    agg = _aggregate_workdays_by_year(all_for_agg)

    lc_ids: set[int] = {annual_lc_id}
    for eid, lc_id, yy in agg.keys():
        if eid == employee_id and yy == y:
            lc_ids.add(lc_id)

    ph = ",".join(["%s"] * len(lc_ids))
    cur.execute(
        f"SELECT id, code, name FROM leave_codes WHERE id IN ({ph})",
        tuple(lc_ids),
    )
    lc_by_id = {int(r["id"]): r for r in (cur.fetchall() or [])}

    items: list[dict] = []
    for lc_id in sorted(lc_ids):
        meta = lc_by_id.get(lc_id)
        if not meta:
            continue
        key = (employee_id, lc_id, y)
        used_records = round(float(agg.get(key, 0.0)), 1)
        if lc_id == annual_lc_id:
            base = round(base_annual_leave_days_kr(hire, ref), 1)
            items.append(
                {
                    "leave_code_id": lc_id,
                    "leave_code": meta["code"],
                    "leave_name": meta["name"],
                    "quota_days": base,
                    "initial_used_days": 0.0,
                    "used_from_records_days": used_records,
                    "used_days": used_records,
                    "remaining_days": round(base - used_records, 1),
                }
            )
        elif used_records > 0:
            items.append(
                {
                    "leave_code_id": lc_id,
                    "leave_code": meta["code"],
                    "leave_name": meta["name"],
                    "quota_days": 0.0,
                    "initial_used_days": 0.0,
                    "used_from_records_days": used_records,
                    "used_days": used_records,
                    "remaining_days": None,
                }
            )
    items.sort(key=lambda x: (str(x["leave_code"]), x["leave_code_id"]))
    total_used = round(sum(float(x["used_days"]) for x in items), 1) if items else 0.0
    if not items:
        total_remaining = None
    else:
        rems = [x["remaining_days"] for x in items]
        total_remaining = (
            round(sum(float(r) for r in rems), 1)
            if all(r is not None for r in rems)
            else None
        )
    return {
        "year": y,
        "items": items,
        "totals": {
            "used_days": total_used,
            "remaining_days": total_remaining,
        },
    }


@router.get("/me/summary")
def my_leave_summary(
    employee_id: int = Depends(get_mobile_employee_id),
    year: Optional[int] = Query(None, description="기준 연도(기본: 올해)"),
    conn: Connection = Depends(get_db),
) -> dict:
    """모바일: 본인 연도별 휴가 배정·사용·잔여 요약."""
    today = date.today()
    y = year if year is not None else today.year
    return _leave_summary_payload(conn, employee_id, y)


@router.get("/employee/{employee_id}/summary")
def employee_leave_summary_for_admin(
    employee_id: int,
    year: Optional[int] = Query(None, description="기준 연도(기본: 올해)"),
    conn: Connection = Depends(get_db),
) -> dict:
    """관리자 화면: 사원별 연도 요약(배정·사용·잔여). 인증 없음(사내 관리 UI)."""
    today = date.today()
    y = year if year is not None else today.year
    cur = conn.cursor(DictCursor)
    cur.execute("SELECT id FROM employees WHERE id = %s LIMIT 1", (employee_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="사원을 찾을 수 없습니다.")
    return _leave_summary_payload(conn, employee_id, y)


@router.get("/employee/{employee_id}/annual-line")
def get_employee_annual_line(
    employee_id: int,
    year: Optional[int] = Query(None, description="기준 연도(기본: 올해)"),
    conn: Connection = Depends(get_db),
) -> dict:
    """관리자: 지정 연차 휴가코드(ANNUAL_LEAVE_CODE) 1줄 — 기준·사용·잔여. 인증 없음."""
    today = date.today()
    y = year if year is not None else today.year
    cur = conn.cursor(DictCursor)
    cur.execute("SELECT id FROM employees WHERE id = %s LIMIT 1", (employee_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="사원을 찾을 수 없습니다.")
    return _annual_line_payload(conn, employee_id, y)


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
    annual_lc_id = _resolve_annual_leave_code_id(conn)
    cur.execute(
        "SELECT id, hire_date FROM employees WHERE id = %s LIMIT 1",
        (employee_id,),
    )
    hr = cur.fetchone()
    hire_by_emp: dict[int, date] = {}
    if hr:
        hire_by_emp[int(employee_id)] = _as_date(hr["hire_date"])
    return [_serialize_row(r, agg, annual_lc_id, hire_by_emp) for r in raw_rows]


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
