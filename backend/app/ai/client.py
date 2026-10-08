import time

from anthropic import Anthropic
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_log import AILog


class AIUnavailable(Exception):
    """Raised when the AI cannot be used (no key, timeout, rate limit, API down)."""


_client: Anthropic | None = None


def _get_client() -> Anthropic:
    global _client
    if not settings.anthropic_api_key:
        raise AIUnavailable("ANTHROPIC_API_KEY is not set")
    if _client is None:
        # max_retries=1: the SDK retries once on timeout / 429 / 5xx
        _client = Anthropic(
            api_key=settings.anthropic_api_key,
            timeout=settings.ai_timeout_seconds,
            max_retries=1,
        )
    return _client


def call_claude(
    db: Session, *, task: str, ticket_id: int | None, system: list[dict], user_text: str, max_tokens: int
) -> str:
    client = _get_client()
    start = time.time()
    try:
        resp = client.messages.create(
            model=settings.ai_model,
            max_tokens=max_tokens,
            temperature=0.2,
            system=system,
            messages=[{"role": "user", "content": user_text}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text")
        _log(db, task, ticket_id, resp.usage.input_tokens, resp.usage.output_tokens, start, True, None)
        return text
    except Exception as e:  # any failure becomes AIUnavailable, caller falls back
        _log(db, task, ticket_id, 0, 0, start, False, str(e)[:500])
        raise AIUnavailable(str(e)) from e


def _log(db, task, ticket_id, tin, tout, start, ok, error):
    db.add(
        AILog(
            ticket_id=ticket_id,
            task=task,
            model=settings.ai_model,
            input_tokens=tin,
            output_tokens=tout,
            latency_ms=int((time.time() - start) * 1000),
            success=ok,
            error=error,
        )
    )
    db.commit()