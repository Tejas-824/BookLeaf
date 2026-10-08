import logging
from datetime import datetime, timezone

from app.ai.classifier import classify
from app.ai.client import AIUnavailable
from app.ai.drafter import generate_draft
from app.db.session import SessionLocal
from app.models.ticket import Ticket

log = logging.getLogger(__name__)


def run_pipeline(ticket_id: int) -> None:
    db = SessionLocal()  # background task needs its own DB session
    try:
        ticket = db.get(Ticket, ticket_id)
        if not ticket:
            return

        # Step 1: classify + priority (one call, with rule fallback)
        result = classify(db, ticket)
        if ticket.category_source == "pending":  # don't overwrite an admin's choice
            ticket.category = result["category"]
            ticket.category_source = result["source"]
        if ticket.priority_source == "pending":
            ticket.priority = result["priority"]
            ticket.priority_source = result["source"]
        if result["source"] == "ai":  # keep AI suggestion only if AI really made it
            ticket.ai_category = result["category"]
            ticket.ai_priority = result["priority"]
        ticket.ai_confidence = result["confidence"]
        db.commit()

        # Step 2: draft reply, saved so we never pay for it twice
        try:
            ticket.ai_draft = generate_draft(db, ticket)
            ticket.ai_draft_at = datetime.now(timezone.utc)
            ticket.ai_status = "ai_done"
        except AIUnavailable as e:
            log.warning("AI draft failed for ticket %s: %s", ticket_id, e)
            ticket.ai_status = "ai_failed"
        db.commit()
    except Exception:
        log.exception("AI pipeline crashed for ticket %s", ticket_id)
        db.rollback()
        t = db.get(Ticket, ticket_id)
        if t:
            t.ai_status = "ai_failed"
            db.commit()
    finally:
        db.close()