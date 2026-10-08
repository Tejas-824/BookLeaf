import time
from collections import defaultdict, deque

from app.core.config import settings
from app.core.errors import AppError

_hits: dict[int, deque] = defaultdict(deque)


def check_ticket_rate_limit(user_id: int) -> None:
    now = time.time()
    q = _hits[user_id]
    while q and now - q[0] > 3600:
        q.popleft()
    if len(q) >= settings.max_tickets_per_hour:
        raise AppError(429, "rate_limited", "You have submitted too many tickets. Please try again in a while.")
    q.append(now)