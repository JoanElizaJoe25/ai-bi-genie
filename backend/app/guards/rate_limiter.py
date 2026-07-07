"""
Rate Limiter Guard.
Max 20 API requests per minute per session.
"""

import time
from collections import defaultdict
from app.config import MAX_REQUESTS_PER_MINUTE

_request_log: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(session_id: str) -> dict:
    now = time.time()
    window_start = now - 60

    _request_log[session_id] = [
        ts for ts in _request_log[session_id]
        if ts > window_start
    ]

    current_count = len(_request_log[session_id])

    if current_count >= MAX_REQUESTS_PER_MINUTE:
        oldest = min(_request_log[session_id])
        retry_after = oldest + 60 - now
        return {
            "is_allowed": False,
            "requests_made": current_count,
            "limit": MAX_REQUESTS_PER_MINUTE,
            "retry_after_seconds": round(max(0, retry_after), 1)
        }

    _request_log[session_id].append(now)

    return {
        "is_allowed": True,
        "requests_made": current_count + 1,
        "limit": MAX_REQUESTS_PER_MINUTE,
        "retry_after_seconds": 0
    }
