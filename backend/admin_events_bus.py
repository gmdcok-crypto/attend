"""In-memory admin event bus for lightweight realtime notifications."""

from __future__ import annotations

from threading import Condition

_cond = Condition()
_seq = 0


def publish_employee_auth_changed(employee_id: int) -> int:
    """Publish employee auth-state change event and return sequence."""
    del employee_id  # reserved for future payload extensions
    global _seq
    with _cond:
        _seq += 1
        _cond.notify_all()
        return _seq


def current_seq() -> int:
    with _cond:
        return _seq


def wait_for_change(last_seq: int, timeout_sec: float) -> int:
    """Block until seq changes or timeout; returns current seq."""
    with _cond:
        if _seq == last_seq:
            _cond.wait(timeout=timeout_sec)
        return _seq
