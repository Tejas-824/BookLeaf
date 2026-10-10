import time
import logging

from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_log import AILog

log = logging.getLogger(__name__)

class AIUnavailable(Exception):
    """Raised when the AI cannot be used (no key, timeout, rate limit, API down)."""

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if not settings.gemini_api_key:
        raise AIUnavailable("GEMINI_API_KEY is not set")
    if _client is None:
        _client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=int(settings.ai_timeout_seconds * 1000)),  # ms
        )
    return _client


def call_llm(
    db: Session, *, task: str, ticket_id: int | None, system: list[dict], user_text: str, max_tokens: int
) -> str:
    client = _get_client()
    system_text = "\n\n".join(block["text"] for block in system)  # join the system parts into one
    config = types.GenerateContentConfig(
        system_instruction=system_text,
        max_output_tokens=max_tokens,
        temperature=0.2,
        # turn off "thinking" so it doesn't use up our small token limit
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    start = time.time()
    last_error = None
    for attempt in range(2):  # 1 try + 1 retry
        try:
            resp = client.models.generate_content(model=settings.ai_model, contents=user_text, config=config)
            if not resp.text:
                raise ValueError("Empty reply from AI (possibly blocked)")
            usage = resp.usage_metadata
            _log(db, task, ticket_id, usage.prompt_token_count or 0,
                 usage.candidates_token_count or 0, start, True, None)
            return resp.text
        except Exception as e:
            last_error = e
            if attempt == 0:
                time.sleep(1)  # short wait, then retry once

        except Exception as e:
            last_error = e
            log.warning("AI call failed (task=%s, attempt=%s): %s", task, attempt + 1, e)        

    _log(db, task, ticket_id, 0, 0, start, False, str(last_error)[:500])
    raise AIUnavailable(str(last_error)) from last_error


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