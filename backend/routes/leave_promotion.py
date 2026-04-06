"""관리자 — 연차촉진 캠페인·대상·발송 표시 (인증 없음, 사내 관리 UI와 동일 정책)."""

from __future__ import annotations

import hashlib
from datetime import date
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.database import Connection, DictCursor, get_db
from backend.routes.employee_leaves import (
    _aggregate_workdays_by_year,
    _load_all_records_for_aggregate,
    _load_quota_maps,
)

router = APIRouter(prefix="/leave-promotion", tags=["leave-promotion"])


def _remaining_total_for_year(conn: Connection, emp_id: int, year: int) -> float | None:
    quotas, initials = _load_quota_maps(conn)
    all_rec = _load_all_records_for_aggregate(conn, [emp_id])
    agg = _aggregate_workdays_by_year(all_rec)
    total_rem = 0.0
    any_q = False
    for key, qv in quotas.items():
        eid, _lc, y = key
        if eid != emp_id or y != year:
            continue
        any_q = True
        used = float(agg.get(key, 0.0)) + float(initials.get(key, 0.0))
        total_rem += float(qv) - used
    if not any_q:
        return None
    return round(total_rem, 1)


def _doc_hash(title: str, doc_version: str, message: str) -> str:
    canonical = f"{title.strip()}\n{doc_version.strip()}\n{message.strip()}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class CampaignCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    doc_version: str = Field(default="v1.0", max_length=32)


class TargetsAdd(BaseModel):
    employee_ids: list[int] = Field(..., min_length=1)


@router.post("/campaigns")
def create_campaign(body: CampaignCreate, conn: Connection = Depends(get_db)) -> dict:
    dh = _doc_hash(body.title, body.doc_version, body.message)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO leave_promotion_campaigns (title, doc_version, message_text, doc_hash)
        VALUES (%s, %s, %s, %s)
        """,
        (body.title.strip(), body.doc_version.strip(), body.message, dh),
    )
    conn.commit()
    return {"id": cur.lastrowid, "doc_hash": dh}


@router.get("/campaigns")
def list_campaigns(conn: Connection = Depends(get_db)) -> list[dict]:
    cur = conn.cursor(DictCursor)
    cur.execute(
        """
        SELECT c.id, c.title, c.doc_version, c.doc_hash, c.created_at,
               COUNT(t.id) AS target_count,
               SUM(CASE WHEN t.signed_at IS NOT NULL THEN 1 ELSE 0 END) AS signed_count,
               SUM(CASE WHEN t.first_sent_at IS NOT NULL THEN 1 ELSE 0 END) AS first_sent_count,
               SUM(CASE WHEN t.second_sent_at IS NOT NULL THEN 1 ELSE 0 END) AS second_sent_count
        FROM leave_promotion_campaigns c
        LEFT JOIN leave_promotion_targets t ON t.campaign_id = c.id
        GROUP BY c.id, c.title, c.doc_version, c.doc_hash, c.created_at
        ORDER BY c.id DESC
        """
    )
    rows = cur.fetchall() or []
    out = []
    for r in rows:
        out.append(
            {
                "id": int(r["id"]),
                "title": r["title"],
                "doc_version": r["doc_version"],
                "doc_hash": r["doc_hash"],
                "created_at": r["created_at"].isoformat() if r.get("created_at") else None,
                "target_count": int(r["target_count"] or 0),
                "signed_count": int(r["signed_count"] or 0),
                "first_sent_count": int(r["first_sent_count"] or 0),
                "second_sent_count": int(r["second_sent_count"] or 0),
            }
        )
    return out


@router.get("/campaigns/{campaign_id}/targets")
def list_targets(
    campaign_id: int,
    year: Optional[int] = Query(None, ge=2000, le=2100),
    status: Optional[Literal["pending", "signed"]] = Query(None),
    conn: Connection = Depends(get_db),
) -> list[dict]:
    cur = conn.cursor(DictCursor)
    cur.execute(
        """
        SELECT c.id FROM leave_promotion_campaigns c WHERE c.id = %s LIMIT 1
        """,
        (campaign_id,),
    )
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="캠페인을 찾을 수 없습니다.")

    y = year if year is not None else date.today().year

    q = """
        SELECT e.id AS employee_id, e.employee_no, e.name,
               d.name AS department_name,
               t.read_at, t.signed_at, t.first_sent_at, t.second_sent_at
        FROM leave_promotion_targets t
        INNER JOIN employees e ON e.id = t.employee_id
        LEFT JOIN departments d ON d.id = e.department_id
        WHERE t.campaign_id = %s
    """
    params: list = [campaign_id]
    if status == "pending":
        q += " AND t.signed_at IS NULL"
    elif status == "signed":
        q += " AND t.signed_at IS NOT NULL"
    q += " ORDER BY e.employee_no"
    cur.execute(q, params)
    rows = cur.fetchall() or []

    out: list[dict] = []
    for r in rows:
        emp_id = int(r["employee_id"])
        try:
            remaining = _remaining_total_for_year(conn, emp_id, y)
        except Exception:
            remaining = None

        ra = r.get("read_at")
        sa = r.get("signed_at")
        fa = r.get("first_sent_at")
        s2 = r.get("second_sent_at")
        out.append(
            {
                "employee_id": emp_id,
                "employee_no": r["employee_no"],
                "name": r["name"],
                "department_name": r.get("department_name"),
                "remaining_days": remaining,
                "read_at": ra.isoformat() if hasattr(ra, "isoformat") else None,
                "signed_at": sa.isoformat() if hasattr(sa, "isoformat") else None,
                "first_sent_at": fa.isoformat() if fa and hasattr(fa, "isoformat") else None,
                "second_sent_at": s2.isoformat() if s2 and hasattr(s2, "isoformat") else None,
            }
        )
    return out


@router.post("/campaigns/{campaign_id}/targets")
def add_targets(
    campaign_id: int,
    body: TargetsAdd,
    conn: Connection = Depends(get_db),
) -> dict:
    cur = conn.cursor(DictCursor)
    cur.execute("SELECT id FROM leave_promotion_campaigns WHERE id = %s", (campaign_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="캠페인을 찾을 수 없습니다.")
    cur2 = conn.cursor()
    added = 0
    for eid in body.employee_ids:
        cur.execute("SELECT id FROM employees WHERE id = %s", (int(eid),))
        if not cur.fetchone():
            continue
        cur2.execute(
            """
            INSERT IGNORE INTO leave_promotion_targets (campaign_id, employee_id)
            VALUES (%s, %s)
            """,
            (campaign_id, int(eid)),
        )
        added += int(cur2.rowcount or 0)
    conn.commit()
    return {"added": added}


@router.post("/campaigns/{campaign_id}/send-first")
def mark_first_send(campaign_id: int, conn: Connection = Depends(get_db)) -> dict:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE leave_promotion_targets
        SET first_sent_at = COALESCE(first_sent_at, CURRENT_TIMESTAMP(3))
        WHERE campaign_id = %s
        """,
        (campaign_id,),
    )
    n = cur.rowcount
    conn.commit()
    return {"updated": n}


@router.post("/campaigns/{campaign_id}/send-second")
def mark_second_send(campaign_id: int, conn: Connection = Depends(get_db)) -> dict:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE leave_promotion_targets
        SET second_sent_at = COALESCE(second_sent_at, CURRENT_TIMESTAMP(3))
        WHERE campaign_id = %s
        """,
        (campaign_id,),
    )
    n = cur.rowcount
    conn.commit()
    return {"updated": n}
