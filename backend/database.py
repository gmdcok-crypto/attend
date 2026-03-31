"""MariaDB 연결 — PyMySQL (순수 Python; Linux CI 에서 Connector/C 빌드 불필요)"""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
from pymysql.err import IntegrityError

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if v is None or v == "":
        raise RuntimeError(f"환경 변수 {name} 가 설정되지 않았습니다.")
    return v


def get_connection() -> Connection:
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=_require_env("DB_USER"),
        password=_require_env("DB_PASSWORD"),
        database=_require_env("DB_NAME"),
        charset="utf8mb4",
    )


def get_db() -> Generator[Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
