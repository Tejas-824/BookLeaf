from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.middleware.rate_limit import check_ticket_rate_limit
from app.models.audit_log import AuditLog
from app.models.book import Book
from app.models.ticket import Ticket
from app.models.ticket_message import TicketMessage
from app.models.user import User
from app.schemas.admin import ReplyCreate, TicketUpdate
from app.schemas.ticket import TicketCreate


def audit(db: Session, ticket_id: int, user_id: int | None, action: str, detail: str | None = None):
    db.add(AuditLog(ticket_id=ticket_id, user_id=user_id, action=action, detail=detail))


def create_ticket(db: Session, user: User, data: TicketCreate, idem_key: str | None) -> tuple[Ticket, bool]:
    """Returns (ticket, created). Saves the ticket FIRST. AI runs later in the background."""
    if idem_key:
        existing = db.scalar(select(Ticket).where(Ticket.idempotency_key == idem_key))
        if existing and existing.author_id == user.author_id:
            return existing, False

    if data.book_id:
        book = db.get(Book, data.book_id)
        if not book or book.author_id != user.author_id:
            raise AppError(404, "book_not_found", "That book was not found in your account.")

    check_ticket_rate_limit(user.id)

    ticket = Ticket(
        author_id=user.author_id,
        book_id=data.book_id,
        subject=data.subject,
        description=data.description,
        attachment_name=data.attachment_name,
        idempotency_key=idem_key,
    )
    db.add(ticket)
    try:
        db.flush()
    except IntegrityError:  # double click race: same key inserted twice
        db.rollback()
        existing = db.scalar(select(Ticket).where(Ticket.idempotency_key == idem_key))
        return existing, False
    audit(db, ticket.id, user.id, "ticket_created")
    db.commit()
    return ticket, True


def apply_update(db: Session, admin: User, ticket: Ticket, data: TicketUpdate) -> Ticket:
    if data.status and data.status != ticket.status:
        audit(db, ticket.id, admin.id, "status_changed", f"{ticket.status} -> {data.status}")
        ticket.status = data.status
    if data.category and data.category != ticket.category:
        audit(db, ticket.id, admin.id, "category_changed", f"{ticket.category} -> {data.category}")
        ticket.category = data.category
        ticket.category_source = "admin"
    if data.priority and data.priority != ticket.priority:
        audit(db, ticket.id, admin.id, "priority_changed", f"{ticket.priority} -> {data.priority}")
        ticket.priority = data.priority
        ticket.priority_source = "admin"
    db.commit()
    return ticket


def add_admin_reply(db: Session, admin: User, ticket: Ticket, data: ReplyCreate) -> Ticket:
    db.add(TicketMessage(ticket_id=ticket.id, sender_role="admin", sender_id=admin.id, body=data.body.strip()))
    ticket.status = data.set_status
    if ticket.assigned_to is None:
        ticket.assigned_to = admin.id
    audit(db, ticket.id, admin.id, "reply_sent", f"status -> {data.set_status}")
    db.commit()
    return ticket