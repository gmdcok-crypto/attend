"""연차촉진 개인별 안내 PDF — 프로젝트 루트 `yuncha.pdf` 양식 + DB 병합."""

from __future__ import annotations

import hashlib
import io
import logging
import math
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from backend.database import Connection, DictCursor

logger = logging.getLogger("attend-api")

KST = ZoneInfo("Asia/Seoul")

ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
FONT_PATH = ASSETS_DIR / "NanumGothic-Regular.ttf"
FONT_URLS = (
    "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Regular.ttf",
)

_FONT_REGISTERED = False

# 사용자 제공 양식 (프로젝트 루트 또는 backend 옆)
YUNCHA_TEMPLATE_PATHS = (
    Path(__file__).resolve().parent.parent / "yuncha.pdf",
    Path(__file__).resolve().parent / "assets" / "yuncha.pdf",
)


def _ensure_korean_font() -> str:
    """Nanum Gothic TTF 캐시 + ReportLab 등록. PyMuPDF·ReportLab 공통 경로 FONT_PATH."""
    global _FONT_REGISTERED
    font_name = "NanumGothic"
    if _FONT_REGISTERED:
        return font_name
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    if not FONT_PATH.is_file() or FONT_PATH.stat().st_size < 10_000:
        last_err: Exception | None = None
        data: bytes | None = None
        for url in FONT_URLS:
            logger.warning("연차촉진 PDF 폰트 캐시 없음 — 다운로드 시도: %s", url)
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "attend-leave-promotion-pdf/1.0"},
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = resp.read()
                if len(data) < 10_000:
                    raise RuntimeError("폰트 응답이 너무 짧습니다.")
                FONT_PATH.write_bytes(data)
                last_err = None
                break
            except Exception as e:
                last_err = e
                logger.error("한글 PDF 폰트 URL 실패 (%s): %s", url, e)
        if last_err is not None or data is None:
            raise RuntimeError(
                "한글 PDF 폰트를 내려받을 수 없습니다. 네트워크·방화벽을 확인하거나 "
                f"수동으로 {FONT_PATH} 에 NanumGothic-Regular.ttf 를 넣어 주세요."
            ) from last_err
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    pdfmetrics.registerFont(TTFont(font_name, str(FONT_PATH)))
    _FONT_REGISTERED = True
    return font_name


def _as_date_str(v: object) -> str:
    if v is None:
        return "—"
    if hasattr(v, "isoformat"):
        return str(v.isoformat())[:10]
    return str(v)[:10]


def _dot_date(v: object) -> str:
    s = _as_date_str(v)
    if s == "—":
        return s
    return s.replace("-", ".")


def _fmt_days(v: object) -> str:
    if v is None:
        return "—"
    try:
        x = float(v)
    except (TypeError, ValueError):
        return str(v)
    if math.isclose(x, round(x), abs_tol=0.05):
        return str(int(round(x)))
    return str(round(x, 1))


def _resolve_yuncha_template() -> Path:
    for p in YUNCHA_TEMPLATE_PATHS:
        if p.is_file():
            return p
    raise RuntimeError(
        "연차촉진 양식 yuncha.pdf 가 없습니다. 프로젝트 루트 또는 backend/assets/ 에 두세요."
    )


def _fill_yuncha_pdf_bytes(emp: dict, annual: dict, year: int) -> bytes:
    import fitz

    _ensure_korean_font()
    font = str(FONT_PATH)
    template = _resolve_yuncha_template()
    doc = fitz.open(template)
    page = doc[0]

    bd = _fmt_days(annual.get("base_days"))
    rem = _fmt_days(annual.get("remaining_days"))
    used = _fmt_days(annual.get("used_days"))
    end_s = f"{year}.12.31"
    period_s = f"{year}.01.01 ~ {year}.12.31"
    occur_s = f"{year}.01.01"

    p1 = (
        f"상기인은 현재 {bd}일의 연차휴가 중 {rem}일의 연차휴가를 사용하여, {end_s}까지 "
        f"{rem}일의 연차 휴가를 추가로 사용할 수 있습니다."
    )

    para_rect = fitz.Rect(72, 326, 528, 382)
    page.add_redact_annot(para_rect, fill=(1, 1, 1))
    page.apply_redactions()
    tw = page.insert_textbox(
        para_rect,
        p1,
        fontfile=font,
        fontsize=10,
        color=(0, 0, 0),
        align=fitz.TEXT_ALIGN_LEFT,
    )
    if tw < 0:
        logger.warning("연차촉진 PDF 본문 텍스트박스 오버플로우 가능")

    name = str(emp.get("name") or "")
    hire = _dot_date(emp.get("hire_date"))

    # yuncha.pdf 레이아웃에 맞춘 좌표 (baseline 근처)
    page.insert_text((165, 168), name, fontfile=font, fontsize=11, color=(0, 0, 0))
    page.insert_text((375, 168), hire, fontfile=font, fontsize=11, color=(0, 0, 0))
    page.insert_text((200, 196), period_s, fontfile=font, fontsize=10, color=(0, 0, 0))
    page.insert_text((200, 224), occur_s, fontfile=font, fontsize=10, color=(0, 0, 0))
    page.insert_text((430, 224), bd, fontfile=font, fontsize=10, color=(0, 0, 0))
    page.insert_text((200, 252), period_s, fontfile=font, fontsize=10, color=(0, 0, 0))
    page.insert_text((200, 280), used, fontfile=font, fontsize=10, color=(0, 0, 0))
    page.insert_text((400, 280), rem, fontfile=font, fontsize=10, color=(0, 0, 0))

    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def build_personalized_pdf_bytes(
    conn: Connection, campaign_id: int, employee_id: int
) -> bytes:
    """캠페인 확인 후 `yuncha.pdf`에 사원·연차(기준연차·사용·잔여) 병합."""
    from backend.routes.employee_leaves import _annual_line_payload

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
        "SELECT 1 FROM leave_promotion_campaigns WHERE id = %s LIMIT 1",
        (campaign_id,),
    )
    if not cur.fetchone():
        raise ValueError("캠페인을 찾을 수 없습니다.")

    today = datetime.now(KST)
    year = today.year
    annual = _annual_line_payload(conn, employee_id, year)

    try:
        return _fill_yuncha_pdf_bytes(dict(emp), annual, year)
    except RuntimeError as e:
        raise RuntimeError(str(e)) from e
    except Exception as e:
        raise RuntimeError(f"PDF 생성 실패: {e!s}") from e


def personalized_pdf_sha256(conn: Connection, campaign_id: int, employee_id: int) -> str:
    b = build_personalized_pdf_bytes(conn, campaign_id, employee_id)
    return hashlib.sha256(b).hexdigest()
