"""MariaDB 연결 — MariaDB Connector/Python"""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import mariadb
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if v is None or v == "":
        raise RuntimeError(f"환경 변수 {name} 가 설정되지 않았습니다.")
    return v


def get_connection() -> mariadb.Connection:
    return mariadb.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=_require_env("DB_USER"),
        password=_require_env("DB_PASSWORD"),
        database=_require_env("DB_NAME"),
    )


def get_db() -> Generator[mariadb.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
