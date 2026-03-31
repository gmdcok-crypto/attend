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


def _find_mysql_url_anywhere() -> tuple[str, int, str, str, str] | None:
    """Railway 등에서 MYSQL_URL 이름이 다르거나, 값만 mysql:// 인 변수가 있을 때."""
    url_keys = (
        "DATABASE_URL",
        "MYSQL_URL",
        "MYSQL_PRIVATE_URL",
        "MYSQL_PUBLIC_URL",
        "MYSQLURL",
        "DATABASE_PRIVATE_URL",
        "DATABASE_PUBLIC_URL",
    )
    for key in url_keys:
        parsed = _parse_mysql_url(os.getenv(key, ""))
        if parsed is not None:
            return parsed
    for _k, v in os.environ.items():
        if not v or len(v) < 15:
            continue
        if not v.startswith(("mysql://", "mariadb://")):
            continue
        parsed = _parse_mysql_url(v)
        if parsed is not None:
            return parsed
    return None


def _db_related_keys_hint() -> str:
    """비밀값 없이 어떤 DB 관련 키가 있는지(이름만)."""
    names = sorted(
        k
        for k in os.environ
        if any(
            x in k.upper()
            for x in ("MYSQL", "DATABASE", "DB_", "MARIA", "SQL")
        )
    )
    if not names:
        return "(DB 관련 환경 변수 이름이 하나도 없습니다.)"
    return ", ".join(names[:40]) + ("…" if len(names) > 40 else "")


def _resolve_db_params() -> tuple[str, int, str, str, str]:
    """우선순위: 아무 mysql:// URL → DB_* → Railway MYSQL*."""
    parsed = _find_mysql_url_anywhere()
    if parsed is not None:
        return parsed

    # Prefer Railway private networking when available. If DB_HOST points to a public proxy,
    # override with MYSQLHOST/MYSQLPORT (internal) to reduce latency and instability.
    db_host = os.getenv("DB_HOST")
    mysql_host = os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST")
    db_port = os.getenv("DB_PORT")
    mysql_port = os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT")

    host = db_host or mysql_host or "127.0.0.1"
    port_str = db_port or mysql_port or "3306"

    if mysql_host and db_host and db_host.endswith(".proxy.rlwy.net"):
        host = mysql_host
        if mysql_port:
            port_str = mysql_port

    try:
        port = int(port_str)
    except ValueError:
        port = 3306

    user = (
        os.getenv("DB_USER")
        or os.getenv("MYSQLUSER")
        or os.getenv("MYSQL_USER")
        or os.getenv("MYSQL_USERNAME")
    )
    password = _env_first("DB_PASSWORD", "MYSQLPASSWORD", "MYSQL_PASSWORD")
    database = _env_first("DB_NAME", "MYSQL_DATABASE", "MYSQLDATABASE")

    if not user:
        raise RuntimeError(
            "DB 사용자(DB_USER / MYSQLUSER)가 없습니다. "
            "Railway 웹(API) 서비스 → Variables 에서 MySQL 서비스 변수를 참조로 추가하세요 "
            "(예: MYSQLUSER, MYSQLPASSWORD, MYSQLHOST, MYSQLDATABASE 또는 MYSQL_URL). "
            f"현재 감지된 관련 키: {_db_related_keys_hint()}"
        )
    if password is None:
        raise RuntimeError(
            "DB 비밀번호(DB_PASSWORD / MYSQLPASSWORD)가 없습니다. "
            f"현재 감지된 관련 키: {_db_related_keys_hint()}"
        )
    if not database:
        raise RuntimeError(
            "DB 이름(DB_NAME / MYSQL_DATABASE)이 없습니다. "
            f"현재 감지된 관련 키: {_db_related_keys_hint()}"
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
        connect_timeout=5,
        read_timeout=30,
        write_timeout=30,
    )


def get_db() -> Generator[Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
