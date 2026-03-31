"""관리자 대시보드 집계 (KST 기준 오늘)."""

from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends

from backend.database import Connection, DictCursor, get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# 지각 판정: 출근(IN) 시각이 09:00:00 초과면 지각 (추후 근무조별로 확장 가능)
_LATE_CUTOFF_SEC = 9 * 3600


@router.get("/summary")
def dashboard_summary(conn: Connection = Depends(get_db)) -> dict:
    cur = conn.cursor(DictCursor)
    cur.execute("SET time_zone = '+09:00'")
    cur.execute("SELECT CURDATE() AS d")
    row = cur.fetchone()
    today: date | str = row["d"] if row else date.today()
    if hasattr(today, "isoformat"):
        today_str = today.isoformat()
    else:
        today_str = str(today)[:10]

    cur.execute(
        """
        SELECT COUNT(DISTINCT employee_id) AS c
        FROM attendance_events
        WHERE event_type = 'IN' AND DATE(occurred_at) = CURDATE()
        """
    )
    today_in = int((cur.fetchone() or {}).get("c") or 0)

    cur.execute(
        """
        SELECT COUNT(*) AS c
        FROM employees e
        WHERE e.status = '재직'
          AND NOT EXISTS (
            SELECT 1 FROM attendance_events a
            WHERE a.employee_id = e.id
              AND a.event_type = 'IN'
              AND DATE(a.occurred_at) = CURDATE()
          )
        """
    )
    not_yet = int((cur.fetchone() or {}).get("c") or 0)

    cur.execute(
        """
        SELECT COUNT(*) AS c FROM (
          SELECT employee_id, MIN(occurred_at) AS first_in
          FROM attendance_events
          WHERE event_type = 'IN' AND DATE(occurred_at) = CURDATE()
          GROUP BY employee_id
        ) t
        WHERE TIME(t.first_in) > '09:00:00'
        """
    )
    late = int((cur.fetchone() or {}).get("c") or 0)

    leave_cnt = 0
    try:
        cur.execute(
            """
            SELECT COUNT(DISTINCT employee_id) AS c
            FROM employee_leave_records
            WHERE CURDATE() BETWEEN start_date AND end_date
            """
        )
        leave_row = cur.fetchone()
        leave_cnt = int(leave_row.get("c") or 0) if leave_row else 0
    except Exception:  # noqa: BLE001 — 휴가 테이블 없을 수 있음
        leave_cnt = 0

    cur.execute(
        """
        SELECT a.occurred_at, a.event_type, e.employee_no, e.name AS employee_name
        FROM attendance_events a
        INNER JOIN employees e ON e.id = a.employee_id
        WHERE DATE(a.occurred_at) = CURDATE()
        ORDER BY a.occurred_at DESC, a.id DESC
        LIMIT 15
        """
    )
    recent_rows = cur.fetchall() or []
    recent: list[dict] = []
    for r in recent_rows:
        oc = r["occurred_at"]
        if hasattr(oc, "isoformat"):
            oc_iso = oc.isoformat(sep=" ", timespec="seconds")
        else:
            oc_iso = str(oc)
        et = r["event_type"]
        status_label = "—"
        if et == "IN":
            if isinstance(oc, datetime):
                sec = oc.hour * 3600 + oc.minute * 60 + oc.second
                status_label = "지각" if sec > _LATE_CUTOFF_SEC else "정상"
            else:
                status_label = "정상"
        elif et == "OUT":
            status_label = "퇴근"
        recent.append(
            {
                "occurred_at": oc_iso,
                "event_type": et,
                "employee_no": r["employee_no"],
                "employee_name": r["employee_name"],
                "status_label": status_label,
            }
        )

    return {
        "date": today_str,
        "today_in_count": today_in,
        "not_yet_in_count": not_yet,
        "late_today_count": late,
        "leave_today_count": leave_cnt,
        "recent": recent,
    }
