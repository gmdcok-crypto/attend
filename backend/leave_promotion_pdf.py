"""연차촉진 개인별 안내 PDF 생성 (DB 데이터 병합 + 한글)."""

from __future__ import annotations

import hashlib
import io
import logging
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.database import Connection, DictCursor

logger = logging.getLogger("attend-api")

KST = ZoneInfo("Asia/Seoul")

ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
FONT_PATH = ASSETS_DIR / "NotoSansKR-Regular.otf"
# Noto Sans KR (OTF, CJK). 최초 1회 로컬 캐시.
FONT_URL = (
    "https://raw.githubusercontent.com/googlefonts/noto-cjk/main/"
    "Sans/OTF/Korean/NotoSansKR-Regular.otf"
)

_FONT_REGISTERED = False


def _ensure_korean_font() -> str:
    """한글 TTF/OTF 등록. 없으면 다운로드 후 캐시."""
    global _FONT_REGISTERED
    font_name = "NotoSansKR"
    if _FONT_REGISTERED:
        return font_name
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    if not FONT_PATH.is_file() or FONT_PATH.stat().st_size < 10_000:
        logger.warning("연차촉진 PDF 폰트 캐시 없음 — 다운로드 시도: %s", FONT_URL)
        try:
            req = urllib.request.Request(
                FONT_URL,
                headers={"User-Agent": "attend-leave-promotion-pdf/1.0"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            if len(data) < 10_000:
                raise RuntimeError("폰트 응답이 너무 짧습니다.")
            FONT_PATH.write_bytes(data)
            logger.warning("NotoSansKR-Regular.otf 저장 완료 (%s bytes)", len(data))
        except Exception as e:
            logger.error("한글 PDF 폰트를 받지 못했습니다: %s", e)
            raise RuntimeError(
                "한글 PDF 폰트를 내려받을 수 없습니다. 네트워크·방화벽을 확인하거나 "
                f"수동으로 {FONT_PATH} 에 NotoSansKR-Regular.otf 를 넣어 주세요."
            ) from e
    pdfmetrics.registerFont(TTFont(font_name, str(FONT_PATH)))
    _FONT_REGISTERED = True
    return font_name


def _as_date_str(v: object) -> str:
    if v is None:
        return "—"
    if hasattr(v, "isoformat"):
        return str(v.isoformat())[:10]
    return str(v)[:10]


def build_personalized_pdf_bytes(
    conn: Connection, campaign_id: int, employee_id: int
) -> bytes:
    """캠페인·사원·휴가 요약을 넣은 1인용 PDF 바이트."""
    from backend.routes.employee_leaves import _leave_summary_payload

    _ensure_korean_font()
    font = "NotoSansKR"

    cur = conn.cursor(DictCursor)
    cur.execute(
        """
        SELECT e.employee_no, e.name, e.hire_date, d.name AS department_name
        FROM employees e
        LEFT JOIN departments d ON d.id = e.department_id
        WHERE e.id = %s
        LIMIT 1
        """,
        (employee_id,),
    )
    emp = cur.fetchone()
    if not emp:
        raise ValueError("사원을 찾을 수 없습니다.")

    cur.execute(
        """
        SELECT id, title, doc_version, message_text, doc_hash
        FROM leave_promotion_campaigns
        WHERE id = %s
        LIMIT 1
        """,
        (campaign_id,),
    )
    camp = cur.fetchone()
    if not camp:
        raise ValueError("캠페인을 찾을 수 없습니다.")

    today = datetime.now(KST)
    y = today.year
    summary = _leave_summary_payload(conn, employee_id, y)
    tot_u = summary.get("totals") or {}
    used_t = tot_u.get("used_days")
    rem_t = tot_u.get("remaining_days")
    used_s = "—" if used_t is None else str(used_t)
    rem_s = "—" if rem_t is None else str(rem_t)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="KTitle",
            fontName=font,
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#111827"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="KBody",
            fontName=font,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1f2937"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="KSmall",
            fontName=font,
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#6b7280"),
        )
    )

    story = []
    story.append(Paragraph(escape(str(camp["title"])), styles["KTitle"]))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            escape(
                f"문서 버전 {camp['doc_version']} · 캠페인 문서 해시 {str(camp['doc_hash'])[:16]}…"
            ),
            styles["KSmall"],
        )
    )
    story.append(Spacer(1, 10))

    meta_data = [
        ["사번", str(emp["employee_no"]), "성명", str(emp["name"])],
        ["부서", str(emp.get("department_name") or "—"), "입사일", _as_date_str(emp.get("hire_date"))],
        [
            "기준 연도",
            str(y),
            "연차 휴가 사용/잔여(요약)",
            f"사용 {used_s}일 / 잔여 {rem_s}일",
        ],
    ]
    t = Table(meta_data, colWidths=[22 * mm, 52 * mm, 28 * mm, 62 * mm])
    t.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), font, 9),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#374151")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f9fafb")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>안내 내용</b>", styles["KBody"]))
    story.append(Spacer(1, 4))

    msg = str(camp.get("message_text") or "").strip()
    for line in msg.splitlines() or [msg]:
        story.append(Paragraph(escape(line) if line else " ", styles["KBody"]))
    story.append(Spacer(1, 14))
    story.append(
        Paragraph(
            escape(
                f"문서 생성: {today.strftime('%Y-%m-%d %H:%M')} (KST) · "
                f"본인 확인·전자서명은 모바일 앱에서 진행합니다."
            ),
            styles["KSmall"],
        )
    )

    doc.build(story)
    raw = buf.getvalue()
    buf.close()
    return raw


def personalized_pdf_sha256(conn: Connection, campaign_id: int, employee_id: int) -> str:
    b = build_personalized_pdf_bytes(conn, campaign_id, employee_id)
    return hashlib.sha256(b).hexdigest()
