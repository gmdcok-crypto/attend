"""
연차휴가 사용 촉구 양식 — 사용자 제공 yuncha.docx 문구·항목에 맞춘 PDF.

개인별 DB 병합은 `leave_promotion_pdf.py` 쪽에서 점진적으로 맞출 수 있음.
"""

from __future__ import annotations

import io
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

from backend.leave_promotion_pdf import _ensure_korean_font

# yuncha.docx 에서 추출한 문구(공백·줄바꿈만 정리)
TITLE = "연차휴가 사용 촉구"

BODY_P1 = (
    "상기인은 현재 일의 연차휴가 중     일의 연차휴가를 사용하여, 20  .  .  .까지    "
    "일의 연차휴가를 추가로 사용할 수 있습니다."
)
BODY_P2 = (
    "상기인은 향후 6개월간 언제 연차휴가를 사용할 것인지 사용 시기를 정하여 10일 이내에 회사로 통보해 주시기 바랍니다. "
    "만약, 연차휴가 사용시기를 회사에 통보하지 않는다면, 회사는 근로기준법에 근거하여 연차휴가 사용기간 마지막 두 달 사이의 일자를 "
    "임의로 연차휴가 사용일로 지정하여 연차사용기간 종료일 2개월 전까지 통보하도록 하겠습니다."
)
BODY_P3 = (
    "상기인이 연차휴가일을 지정하지 않고, 회사가 지정한 연차휴가일에 연차휴가를 사용하지 않는 경우, "
    "근로기준법에 따라 해당 연차휴가는 소멸하며, 수당도 지급되지 않음에 유의하시기 바랍니다."
)

SAMPLE_OUT = Path(__file__).resolve().parent / "assets" / "samples" / "yuncha_form_template.pdf"


def build_yuncha_form_pdf_bytes() -> bytes:
    """정적 양식 PDF (워드와 동일 문구)."""
    font = _ensure_korean_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            name="YTitle",
            parent=base["Normal"],
            fontName=font,
            fontSize=15,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111827"),
            spaceAfter=14,
        ),
        "label": ParagraphStyle(
            name="YLabel",
            parent=base["Normal"],
            fontName=font,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#111827"),
        ),
        "blank": ParagraphStyle(
            name="YBlank",
            parent=base["Normal"],
            fontName=font,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#6b7280"),
        ),
        "body": ParagraphStyle(
            name="YBody",
            parent=base["Normal"],
            fontName=font,
            fontSize=9.5,
            leading=14,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor("#1f2937"),
            spaceAfter=10,
        ),
        "sign": ParagraphStyle(
            name="YSign",
            parent=base["Normal"],
            fontName=font,
            fontSize=10,
            leading=16,
            textColor=colors.HexColor("#111827"),
        ),
        "rep": ParagraphStyle(
            name="YRep",
            parent=base["Normal"],
            fontName=font,
            fontSize=10.5,
            leading=16,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#111827"),
            spaceBefore=8,
        ),
    }

    story: list = []
    story.append(Paragraph(escape(TITLE), styles["title"]))
    story.append(Spacer(1, 4 * mm))

    field_rows = [
        ("이름", "________________________________"),
        ("입사일", "________________________________"),
        ("연차휴가 산정기간", "20  .  .  .  ~  20  .  .  ."),
        ("연차휴가 발생시점", "________________________________"),
        ("발생 연차휴가 일수", "________________________ 일"),
        ("연차휴가 사용기간", "20  .  .  .  ~  20  .  .  ."),
        ("사용한 연차 일수", "________________________________"),
        ("남은 연차 일수", "________________________________"),
    ]
    t_data: list[list] = []
    for lab, val in field_rows:
        t_data.append(
            [
                Paragraph(escape(lab), styles["label"]),
                Paragraph(escape(val), styles["blank"]),
            ]
        )
    tbl = Table(t_data, colWidths=[42 * mm, 118 * mm])
    tbl.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), font, 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LINEBELOW", (0, 0), (-1, -2), 0.25, colors.HexColor("#e5e7eb")),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 8 * mm))

    for ptxt in (BODY_P1, BODY_P2, BODY_P3):
        story.append(Paragraph(escape(ptxt), styles["body"]))

    story.append(Spacer(1, 12 * mm))
    story.append(
        Paragraph(escape("확인자           (서명 또는 날인) ________________________________"), styles["sign"])
    )
    story.append(Paragraph(escape("0000 대표"), styles["rep"]))

    doc.build(story)
    return buf.getvalue()


def write_sample_pdf(path: Path | None = None) -> Path:
    """샘플 PDF 파일 기록. 기본: backend/assets/samples/yuncha_form_template.pdf"""
    out = path or SAMPLE_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(build_yuncha_form_pdf_bytes())
    return out


if __name__ == "__main__":
    p = write_sample_pdf()
    print(f"Wrote: {p} ({p.stat().st_size} bytes)")
