from __future__ import annotations

from fastapi import APIRouter

from backend.kiosk_qr import mint_kiosk_qr_payload

router = APIRouter(prefix="/kiosk", tags=["kiosk"])


@router.get("/attendance-qr")
def get_attendance_qr() -> dict:
    """태블릿·키오스크가 주기적으로 호출해 QR에 넣을 서명 페이로드를 받습니다."""
    return mint_kiosk_qr_payload()
