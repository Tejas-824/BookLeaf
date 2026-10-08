import json
import re

from sqlalchemy.orm import Session

from app.ai.client import AIUnavailable, call_claude
from app.ai.fallback import rule_classify
from app.ai.prompts import CLASSIFIER_SYSTEM
from app.core.config import settings
from app.core.constants import CATEGORIES, PRIORITIES
from app.models.ticket import Ticket


def _parse(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON in AI reply")
    data = json.loads(match.group(0))
    if data.get("category") not in CATEGORIES or data.get("priority") not in PRIORITIES:
        raise ValueError("AI returned invalid category or priority")
    confidence = data.get("confidence") if data.get("confidence") in ("high", "medium", "low") else "medium"
    return {"category": data["category"], "priority": data["priority"], "confidence": confidence}


def classify(db: Session, ticket: Ticket) -> dict:
    """Never raises. Falls back to keyword rules if AI fails."""
    limit = settings.max_ticket_chars_for_ai
    user_text = f"<ticket>\nSubject: {ticket.subject}\n{ticket.description[:limit]}\n</ticket>"
    system = [{"type": "text", "text": CLASSIFIER_SYSTEM, "cache_control": {"type": "ephemeral"}}]
    try:
        text = call_claude(
            db, task="classify", ticket_id=ticket.id, system=system, user_text=user_text, max_tokens=80
        )
        return {**_parse(text), "source": "ai"}
    except (AIUnavailable, ValueError, json.JSONDecodeError):
        category, priority = rule_classify(ticket.subject, ticket.description)
        return {"category": category, "priority": priority, "confidence": "low", "source": "rule"}