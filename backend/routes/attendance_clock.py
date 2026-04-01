"""모바일 QR 출퇴근 기록."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from backend.database import Connection, DictCursor, get_db
from backend.deps_mobile import get_mobile_employee_id
from backend.kiosk_qr import verify_kiosk_qr_payload

router = APIRouter(prefix="/attendance", tags=["attendance"])


class ClockQrBody(BaseModel):
    qr: str = Field(..., min_length=1, description="스캔한 QR 문자열(JSON)")
    intent: Literal["in", "out"]


def _dt_iso(v: Any) -> str:
    if isinstance(v, datetime):
        return v.isoformat(sep=" ", timespec="seconds")
    return str(v)


def _today_type_count(conn: Connection, employee_id: int, event_type: str) -> int:
    cur = conn.cursor(DictCursor)
    cur.execute("SET time_zone = '+09:00'")
    cur.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM attendance_events
        WHERE employee_id = %s
          AND event_type = %s
          AND DATE(occurred_at) = CURDATE()
        """,
        (employee_id, event_type),
    )
    row = cur.fetchone() or {}
    return int(row.get("cnt") or 0)


@router.get("/today")
def attendance_today(
    employee_id: int = Depends(get_mobile_employee_id),
    conn: Connection = Depends(get_db),
) -> dict:
    """오늘(KST) 본인 출퇴근 이벤트 요약."""
    cur = conn.cursor(DictCursor)
    cur.execute("SET time_zone = '+09:00'")
    cur.execute(
        """
        SELECT event_type, occurred_at
        FROM attendance_events
        WHERE employee_id = %s AND DATE(occurred_at) = CURDATE()
        ORDER BY occurred_at ASC, id ASC
        """,
        (employee_id,),
    )
    rows = cur.fetchall() or []

    clocked_in = False
    last_in_at: Optional[str] = None
    last_out_at: Optional[str] = None
    for r in rows:
        et = r["event_type"]
        oc = r["occurred_at"]
        if et == "IN":
            clocked_in = True
            last_in_at = _dt_iso(oc)
        elif et == "OUT":
            clocked_in = False
            last_out_at = _dt_iso(oc)

    return {
        "clocked_in": clocked_in,
        "last_in_at": last_in_at,
        "last_out_at": last_out_at,
    }


@router.post("/clock-qr")
def clock_with_qr(
    body: ClockQrBody,
    request: Request,
    employee_id: int = Depends(get_mobile_employee_id),
    conn: Connection = Depends(get_db),
) -> dict:
    raw_s = body.qr.strip()
    try:
        data = json.loads(raw_s)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail="QR 내용을 JSON으로 읽을 수 없습니다.") from e
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="QR 데이터 형식이 올바르지 않습니다.")

    verify_kiosk_qr_payload(data)

    intent = body.intent
    event_type = "IN" if intent == "in" else "OUT"

    cur = conn.cursor(DictCursor)
    cur.execute("SET time_zone = '+09:00'")
    cur.execute(
        """
        SELECT event_type, occurred_at
        FROM attendance_events
        WHERE employee_id = %s AND DATE(occurred_at) = CURDATE()
        ORDER BY occurred_at DESC, id DESC
        LIMIT 1
        """,
        (employee_id,),
    )
    last = cur.fetchone()
    last_type = last["event_type"] if last else None

    if intent == "in":
        if _today_type_count(conn, employee_id, "IN") >= 1:
            raise HTTPException(status_code=409, detail="오늘 출근은 1회만 가능합니다.")
        if last_type == "IN":
            raise HTTPException(
                status_code=409,
                detail="오늘 이미 출근 처리되었습니다. 퇴근 후 다시 시도하세요.",
            )
    else:
        if _today_type_count(conn, employee_id, "OUT") >= 1:
            raise HTTPException(status_code=409, detail="오늘 퇴근은 1회만 가능합니다.")
        if last_type != "IN":
            raise HTTPException(
                status_code=409,
                detail="출근 기록이 없어 퇴근할 수 없습니다.",
            )

    if last:
        cur.execute(
            """
            SELECT id FROM attendance_events
            WHERE employee_id = %s AND event_type = %s
              AND occurred_at >= NOW(3) - INTERVAL 45 SECOND
            ORDER BY occurred_at DESC
            LIMIT 1
            """,
            (employee_id, event_type),
        )
        if cur.fetchone():
            raise HTTPException(status_code=429, detail="잠시 후 다시 시도하세요.")

    ua = (request.headers.get("user-agent") or "")[:250]
    ins = conn.cursor()
    ins.execute(
        """
        INSERT INTO attendance_events (employee_id, event_type, occurred_at, source, device_info)
        VALUES (%s, %s, NOW(3), 'QR', %s)
        """,
        (employee_id, event_type, ua or None),
    )
    new_id = ins.lastrowid
    conn.commit()

    cur_sel = conn.cursor(DictCursor)
    cur_sel.execute(
        "SELECT occurred_at FROM attendance_events WHERE id = %s",
        (new_id,),
    )
    row = cur_sel.fetchone()
    occurred = row["occurred_at"] if row else None

    return {
        "ok": True,
        "event_type": event_type,
        "occurred_at": _dt_iso(occurred) if occurred is not None else None,
    }
