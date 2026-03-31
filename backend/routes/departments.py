from __future__ import annotations

import re
from typing import Optional

import mariadb
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.database import get_db

router = APIRouter(prefix="/departments", tags=["departments"])


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    code: Optional[str] = None


class DepartmentUpdate(BaseModel):
    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


def _next_dept_code(conn: mariadb.Connection) -> str:
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT code FROM departments")
    max_n = 0
    for row in cur.fetchall() or []:
        m = re.match(r"^D(\d+)$", row["code"], re.I)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"D{max_n + 1:03d}"


@router.get("")
def list_departments(conn: mariadb.Connection = Depends(get_db)) -> list[dict]:
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, code, name FROM departments ORDER BY code")
    return list(cur.fetchall() or [])


@router.post("", status_code=201)
def create_department(body: DepartmentCreate, conn: mariadb.Connection = Depends(get_db)) -> dict:
    name = body.name.strip()
    code = (body.code or "").strip() or _next_dept_code(conn)
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO departments (code, name) VALUES (%s, %s)", (code, name))
        conn.commit()
        new_id = cur.lastrowid
    except mariadb.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=409, detail=str(e)) from e
    return {"id": int(new_id), "code": code, "name": name}


@router.put("/{dept_id}")
def update_department(
    dept_id: int, body: DepartmentUpdate, conn: mariadb.Connection = Depends(get_db)
) -> dict:
    cur = conn.cursor()
    cur.execute(
        "UPDATE departments SET code=%s, name=%s WHERE id=%s",
        (body.code.strip(), body.name.strip(), dept_id),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


@router.delete("/{dept_id}", status_code=204)
def delete_department(dept_id: int, conn: mariadb.Connection = Depends(get_db)) -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM departments WHERE id=%s", (dept_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="not found")
