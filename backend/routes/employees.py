from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.database import Connection, DictCursor, IntegrityError, get_db
from backend.admin_events_bus import publish_employee_auth_changed
from backend.passwords import hash_password

router = APIRouter(prefix="/employees", tags=["employees"])


class EmployeeCreate(BaseModel):
    employee_no: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    department_name: str = Field(..., min_length=1)
    hire_date: str = Field(..., min_length=1)
    status: str = Field(default="재직")


class EmployeeUpdate(BaseModel):
    employee_no: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    department_name: str = Field(..., min_length=1)
    hire_date: str = Field(..., min_length=1)
    status: str = Field(default="재직")


class PasswordResetBody(BaseModel):
    new_password: str = Field(..., min_length=1)


def _resolve_department_id(conn: Connection, dept_key: str) -> Optional[int]:
    cur = conn.cursor(DictCursor)
    cur.execute(
        "SELECT id FROM departments WHERE name = %s OR code = %s LIMIT 1",
        (dept_key, dept_key),
    )
    row = cur.fetchone()
    return int(row["id"]) if row else None


def _serialize_emp(row: dict) -> dict:
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


_SELECT_EMP = """
    SELECT e.id, e.employee_no, e.name, e.hire_date, e.status, e.auth_status, d.name AS department_name
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id
"""


@router.get("/by-number/{employee_no}")
def get_employee_by_number(
    employee_no: str, conn: Connection = Depends(get_db)
) -> dict:
    cur = conn.cursor(DictCursor)
    cur.execute(
        _SELECT_EMP + " WHERE e.employee_no = %s LIMIT 1",
        (employee_no.strip(),),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="사원을 찾을 수 없습니다.")
    return _serialize_emp(row)


@router.get("")
def list_employees(
    conn: Connection = Depends(get_db),
    status: Optional[str] = Query(None, description="예: 재직"),
) -> list[dict]:
    cur = conn.cursor(DictCursor)
    if status:
        cur.execute(
            _SELECT_EMP + " WHERE e.status = %s ORDER BY e.employee_no",
            (status,),
        )
    else:
        cur.execute(_SELECT_EMP + " ORDER BY e.employee_no")
    return [_serialize_emp(r) for r in (cur.fetchall() or [])]


@router.post("", status_code=201)
def create_employee(body: EmployeeCreate, conn: Connection = Depends(get_db)) -> dict:
    dept_id = _resolve_department_id(conn, body.department_name.strip())
    if dept_id is None:
        raise HTTPException(status_code=400, detail="부서를 찾을 수 없습니다. 부서명 또는 부서코드를 확인하세요.")
    try:
        hd = date.fromisoformat(body.hire_date[:10])
    except ValueError as e:
        raise HTTPException(status_code=400, detail="입사일 형식이 올바르지 않습니다.") from e

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO employees (employee_no, name, department_id, hire_date, status, password_hash, auth_status)
            VALUES (%s, %s, %s, %s, %s, NULL, 'X')
            """,
            (
                body.employee_no.strip(),
                body.name.strip(),
                dept_id,
                hd,
                body.status.strip() or "재직",
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
    except IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=409, detail=str(e)) from e
    return {"id": int(new_id)}


@router.put("/{emp_id}")
def update_employee(
    emp_id: int, body: EmployeeUpdate, conn: Connection = Depends(get_db)
) -> dict:
    dept_id = _resolve_department_id(conn, body.department_name.strip())
    if dept_id is None:
        raise HTTPException(status_code=400, detail="부서를 찾을 수 없습니다.")
    try:
        hd = date.fromisoformat(body.hire_date[:10])
    except ValueError as e:
        raise HTTPException(status_code=400, detail="입사일 형식이 올바르지 않습니다.") from e
    cur = conn.cursor(DictCursor)
    cur.execute("SELECT id FROM employees WHERE id = %s LIMIT 1", (emp_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="사원을 찾을 수 없습니다.")
    cur.execute(
        """
        UPDATE employees
        SET employee_no=%s, name=%s, department_id=%s, hire_date=%s, status=%s
        WHERE id=%s
        """,
        (
            body.employee_no.strip(),
            body.name.strip(),
            dept_id,
            hd,
            body.status.strip() or "재직",
            emp_id,
        ),
    )
    conn.commit()
    # 값이 동일하면 MySQL 이 영향 행 수 0 을 줄 수 있어 rowcount 로 404 를 내지 않는다.
    publish_employee_auth_changed(emp_id)
    return {"ok": True}


@router.post("/{emp_id}/revoke-auth")
def revoke_employee_auth(emp_id: int, conn: Connection = Depends(get_db)) -> dict:
    """비밀번호 제거 + 미인증. 모바일에서 비밀번호 분실 시 재설정 절차용."""
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE employees
        SET password_hash=NULL, auth_status='X'
        WHERE id=%s
        """,
        (emp_id,),
    )
    cur.execute(
        """
        UPDATE mobile_refresh_tokens
        SET revoked_at = NOW(3)
        WHERE employee_id=%s AND revoked_at IS NULL
        """,
        (emp_id,),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
    publish_employee_auth_changed(emp_id)
    return {"ok": True}


@router.post("/{emp_id}/reset-password")
def reset_employee_password(
    emp_id: int, body: PasswordResetBody, conn: Connection = Depends(get_db)
) -> dict:
    pwd_hash = hash_password(body.new_password.strip())
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE employees
        SET password_hash=%s, auth_status='X'
        WHERE id=%s
        """,
        (pwd_hash, emp_id),
    )
    cur.execute(
        """
        UPDATE mobile_refresh_tokens
        SET revoked_at = NOW(3)
        WHERE employee_id=%s AND revoked_at IS NULL
        """,
        (emp_id,),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


@router.delete("/{emp_id}", status_code=204)
def delete_employee(emp_id: int, conn: Connection = Depends(get_db)) -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM employees WHERE id=%s", (emp_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
