from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from backend.admin_events_bus import current_seq, wait_for_change

router = APIRouter(prefix="/admin/events", tags=["admin-events"])


@router.get("")
async def admin_events_stream(request: Request):
    async def event_generator():
        last_seq = current_seq()
        while True:
            if await request.is_disconnected():
                break
            seq = await asyncio.to_thread(wait_for_change, last_seq, 20.0)
            if seq == last_seq:
                # keep-alive comment frame
                yield ": keep-alive\n\n"
                continue
            last_seq = seq
            payload = json.dumps({"topic": "employee_auth", "seq": seq}, ensure_ascii=False)
            yield f"event: employee_auth\ndata: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
