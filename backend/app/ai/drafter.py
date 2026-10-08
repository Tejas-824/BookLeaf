from sqlalchemy.orm import Session

from app.ai.client import call_claude
from app.ai.knowledge_base import get_kb_context
from app.ai.prompts import DRAFT_SYSTEM
from app.core.config import settings
from app.models.ticket import Ticket
from app.services.royalty_service import build_facts_text


def _recent_history(ticket: Ticket) -> str:
    # Only the last 2 messages, trimmed. We never send the full history.
    if not ticket.messages:
        return ""
    lines = [f"{m.sender_role}: {m.body[:500]}" for m in ticket.messages[-2:]]
    return "<previous_messages>\n" + "\n".join(lines) + "\n</previous_messages>\n\n"


def generate_draft(db: Session, ticket: Ticket) -> str:
    category = ticket.category or "General Inquiry"
    facts = build_facts_text(ticket.author, ticket.book)

    user_text = (
        f"<author_data>\n{facts}\n</author_data>\n\n"
        f"{_recent_history(ticket)}"
        f"<ticket>\nSubject: {ticket.subject}\n{ticket.description[: settings.max_ticket_chars_for_ai]}\n</ticket>\n\n"
        "Write the reply to this ticket now."
    )
    system = [
        # Fixed part, same for every call, so Anthropic can cache it
        {"type": "text", "text": DRAFT_SYSTEM, "cache_control": {"type": "ephemeral"}},
        # Only the KB sections relevant to this category
        {"type": "text", "text": f"<policy>\n{get_kb_context(category)}\n</policy>"},
    ]
    return call_claude(
        db, task="draft", ticket_id=ticket.id, system=system, user_text=user_text, max_tokens=500
    ).strip()