"""근태 API — MariaDB(PyMySQL) + KST 세션"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from backend.database import DictCursor, get_connection
from backend.routes import (
    attendance,
    attendance_clock,
    auth_mobile,
    dashboard,
    departments,
    employee_leaves,
    employees,
    kiosk,
    leave_codes,
    work_shifts,
)
from backend.schema_ensure import (
    ensure_employee_auth_columns,
    ensure_employee_leave_tables,
    ensure_work_shift_types_table,
)

# database.py 에서도 load 하지만, 단독 실행 시 대비
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger("attend-api")


def _root_log_level() -> int:
    if os.getenv("LOG_LEVEL"):
        return getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_SERVICE_NAME"):
        return logging.WARNING
    return logging.INFO


logging.basicConfig(
    level=_root_log_level(),
    format="%(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    conn = get_connection()
    try:
        try:
            if ensure_employee_auth_columns(conn):
                conn.commit()
                logger.warning(
                    "employees 테이블에 password_hash / auth_status 컬럼을 추가했습니다."
                )
            if ensure_employee_leave_tables(conn):
                conn.commit()
                logger.warning("개인별 휴가 테이블(employee_leave_*)을 생성했습니다.")
            if ensure_work_shift_types_table(conn):
                conn.commit()
                logger.warning("근무시간 유형 테이블(work_shift_types)을 생성했습니다.")
        except Exception as e:  # noqa: BLE001
            conn.rollback()
            logger.error("스키마 보강 실패 (DB 확인): %s", e)
            raise
        yield
    finally:
        conn.close()


app = FastAPI(title="attend-api", version="0.1.0", lifespan=_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_mobile.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(departments.router, prefix="/api")
app.include_router(leave_codes.router, prefix="/api")
app.include_router(employee_leaves.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
app.include_router(attendance_clock.router, prefix="/api")
app.include_router(kiosk.router, prefix="/api")
app.include_router(work_shifts.router, prefix="/api")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    if os.getenv("DEBUG_TRACEBACK", "").lower() in ("1", "true", "yes"):
        import traceback

        traceback.print_exc()
    else:
        logger.error("unhandled %s: %s", type(exc).__name__, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_type": type(exc).__name__},
    )


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "service": "attend-api",
        "stack": "fastapi",
        "dbConnector": "PyMySQL",
    }


@app.get("/api/db/ping", response_model=None)
def db_ping() -> Union[dict, JSONResponse]:
    try:
        conn = get_connection()
        try:
            cur = conn.cursor(DictCursor)
            cur.execute("SET time_zone = '+09:00'")
            cur.execute("SELECT NOW() AS db_now, @@session.time_zone AS tz")
            row = cur.fetchone()
        finally:
            conn.close()

        db_now = row.get("db_now") if row else None
        now_str: str | None
        if isinstance(db_now, datetime):
            now_str = db_now.isoformat()
        elif db_now is not None:
            now_str = str(db_now)
        else:
            now_str = None

        return {
            "ok": True,
            "db": os.getenv("DB_NAME"),
            "sessionTimeZone": row.get("tz") if row else None,
            "nowKstSession": now_str,
        }
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
