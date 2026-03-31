"""MariaDB 연결 — PyMySQL (순수 Python; Linux CI 에서 Connector/C 빌드 불필요)"""

from __future__ import annotations

import os
import re
from collections.abc import Generator
from pathlib import Path
from urllib.parse import unquote, urlparse

import pymysql
from dotenv import load_dotenv
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
from pymysql.err import IntegrityError

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")


def _env_first(*keys: str) -> str | None:
    """첫 번째로 os.environ 에 존재하는 키의 값(빈 문자열 포함). 없으면 None."""
    for k in keys:
        if k in os.environ:
            return os.environ[k]
    return None


def _parse_mysql_url(url: str) -> tuple[str, int, str, str, str] | None:
    """mysql:// 또는 mariadb:// URL → (host, port, user, password, database)."""
    if not url or not re.match(r"^(mysql|mariadb)(\+[^:]+)?://", url, re.I):
        return None
    parsed = urlparse(url)
    if not parsed.hostname:
        return None
    user = unquote(parsed.username or "")
    password = unquote(parsed.password or "")
    db = (parsed.path or "").lstrip("/").split("/")[0]
    port = parsed.port or 3306
    if not user or not db:
        return None
    return parsed.hostname, port, user, password, db


def _resolve_db_params() -> tuple[str, int, str, str, str]:
    """우선순위: DATABASE_URL / MYSQL_URL → DB_* → Railway MYSQL_*."""
    for key in ("DATABASE_URL", "MYSQL_URL", "MYSQL_PRIVATE_URL", "MYSQL_PUBLIC_URL"):
        parsed = _parse_mysql_url(os.getenv(key, ""))
        if parsed is not None:
            return parsed

    host = (
        os.getenv("DB_HOST")
        or os.getenv("MYSQLHOST")
        or os.getenv("MYSQL_HOST")
        or "127.0.0.1"
    )
    port_str = (
        os.getenv("DB_PORT")
        or os.getenv("MYSQLPORT")
        or os.getenv("MYSQL_PORT")
        or "3306"
    )
    try:
        port = int(port_str)
    except ValueError:
        port = 3306

    user = os.getenv("DB_USER") or os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER")
    password = _env_first("DB_PASSWORD", "MYSQLPASSWORD", "MYSQL_PASSWORD")
    database = _env_first("DB_NAME", "MYSQL_DATABASE", "MYSQLDATABASE")

    if not user:
        raise RuntimeError(
            "DB 사용자가 설정되지 않았습니다. "
            "Railway Variables 에 DB_USER 또는 MYSQLUSER 를 설정하거나, "
            "MySQL 플러그인을 서비스에 연결해 MYSQL_* 변수를 주입하세요."
        )
    if password is None:
        raise RuntimeError(
            "DB 비밀번호가 설정되지 않았습니다. "
            "DB_PASSWORD 또는 MYSQLPASSWORD 를 설정하세요."
        )
    if not database:
        raise RuntimeError(
            "DB 이름이 설정되지 않았습니다. "
            "DB_NAME 또는 MYSQL_DATABASE(MYSQLDATABASE) 를 설정하세요."
        )

    return host, port, user, password, database


def get_connection() -> Connection:
    host, port, user, password, database = _resolve_db_params()
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
    )


def get_db() -> Generator[Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
