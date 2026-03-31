"""
Apply sql/*.sql (sorted by filename) to MariaDB using MariaDB Connector/Python.

Usage (from project root):
  python scripts/apply_schema.py

Requires: pip install -r backend/requirements.txt (mariadb, python-dotenv)
Loads:    .env in project root (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = ROOT / "sql"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.schema_ensure import ensure_employee_auth_columns  # noqa: E402


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if v is None or v == "":
        print(f"ERROR: missing env {name}", file=sys.stderr)
        sys.exit(1)
    return v


def _strip_sql_comments(sql: str) -> str:
    lines_out: list[str] = []
    for line in sql.splitlines():
        s = line.strip()
        if s.startswith("--"):
            continue
        if "--" in line:
            line = line[: line.index("--")]
        lines_out.append(line)
    return "\n".join(lines_out)


def _split_statements(sql: str) -> list[str]:
    sql = _strip_sql_comments(sql)
    parts = re.split(r";\s*", sql)
    return [p.strip() for p in parts if p.strip()]


def main() -> None:
    load_dotenv(dotenv_path=ROOT / ".env")

    sql_files = sorted(SQL_DIR.glob("*.sql"))
    if not sql_files:
        print(f"ERROR: no SQL files in {SQL_DIR}", file=sys.stderr)
        sys.exit(1)

    import mariadb

    conn = mariadb.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=_require_env("DB_USER"),
        password=_require_env("DB_PASSWORD"),
        database=_require_env("DB_NAME"),
    )

    try:
        cur = conn.cursor()
        stmt_idx = 0
        for sql_path in sql_files:
            sql_text = sql_path.read_text(encoding="utf-8")
            statements = _split_statements(sql_text)
            print(f"--- {sql_path.name} ({len(statements)} statements)")
            for stmt in statements:
                stmt_idx += 1
                cur.execute(stmt)
                print(f"OK ({stmt_idx}) {stmt[:72].replace(chr(10), ' ')}...")
        print("--- ensure employees auth columns")
        if ensure_employee_auth_columns(conn):
            print("OK: employees.password_hash / auth_status 보강됨")
        conn.commit()
        cur.execute(
            """
            SELECT TABLE_NAME FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
            """
        )
        tables = [row[0] for row in cur.fetchall()]
        print("---")
        print("Tables in database:", ", ".join(tables) if tables else "(none)")
        print("Schema apply finished.")
    except Exception as e:  # noqa: BLE001
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
