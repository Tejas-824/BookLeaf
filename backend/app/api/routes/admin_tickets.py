from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.ai.client import AIUnavailable
from app.ai.drafter import generate_draft
from app.core.constants import OVERDUE_HOURS, Category, Priority, Status
from app.core.deps import require_admin
from app.core.errors import AppError
from app.db.session import get_db
from app.models.internal_note import InternalNote
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.admin import AdminTicketDetail, NoteCreate, NoteOut, ReplyCreate, TicketUpdate
from app.services.ticket_service import add_admin_reply, apply_update, audit

router = APIRouter(prefix="/api/admin/tickets", tags=["Admin: Tickets"])

PRIORITY_RANK = case({"Critical": 0, "High": 1, "Medium": 2, "Low": 3}, value=Ticket.priority, else_=2)
IS_DONE = case((Ticket.status.in_(("Resolved", "Closed")), 1), else_=0)


def _age_hours(created_at: datetime) -> float:
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - created_at).total_seconds() / 3600


def _get_ticket(db: Session, ticket_id: int) -> Ticket:
    ticket = db.scalar(
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(
            selectinload(Ticket.messages),
            selectinload(Ticket.notes),
            joinedload(Ticket.author),
            joinedload(Ticket.book),
        )
    )
    if not ticket:
        raise AppError(404, "ticket_not_found", "Ticket not found.")
    return ticket


@router.get("")
def ticket_queue(
    status: Status | None = None,
    category: Category | None = None,
    priority: Priority | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    mine: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),  # pagination: never load everything
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    filters = []
    if status:
        filters.append(Ticket.status == status)
    if category:
        filters.append(Ticket.category == category)
    if priority:
        filters.append(Ticket.priority == priority)
    if date_from:
        filters.append(Ticket.created_at >= datetime.combine(date_from, time.min))
    if date_to:
        filters.append(Ticket.created_at < datetime.combine(date_to + timedelta(days=1), time.min))
    if mine:
        filters.append(Ticket.assigned_to == admin.id)

    total = db.scalar(select(func.count(Ticket.id)).where(*filters))
    rows = db.scalars(
        select(Ticket)
        .where(*filters)
        .options(joinedload(Ticket.author))
        # open tickets first, then most urgent, then oldest first
        .order_by(IS_DONE, PRIORITY_RANK, Ticket.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = []
    for t in rows:
        age = _age_hours(t.created_at)
        items.append(
            {
                "id": t.id,
                "subject": t.subject,
                "author_id": t.author_id,
                "author_name": t.author.name,
                "status": t.status,
                "category": t.category,
                "category_source": t.category_source,
                "priority": t.priority,
                "priority_source": t.priority_source,
                "ai_status": t.ai_status,
                "assigned_to": t.assigned_to,
                "created_at": t.created_at,
                "age_hours": round(age, 1),
                "overdue": t.status in ("Open", "In Progress") and age > OVERDUE_HOURS,
            }
        )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{ticket_id}", response_model=AdminTicketDetail)
def ticket_detail(ticket_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return _get_ticket(db, ticket_id)  # includes cached ai_draft, so no new AI call here


@router.patch("/{ticket_id}", response_model=AdminTicketDetail)
def update_ticket(
    ticket_id: int, body: TicketUpdate, admin: User = Depends(require_admin), db: Session = Depends(get_db)
):
    ticket = _get_ticket(db, ticket_id)
    apply_update(db, admin, ticket, body)
    return ticket


@router.post("/{ticket_id}/assign-me", response_model=AdminTicketDetail)
def assign_to_me(ticket_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    ticket = _get_ticket(db, ticket_id)
    ticket.assigned_to = admin.id
    audit(db, ticket.id, admin.id, "assigned", f"assigned to user {admin.id}")
    db.commit()
    return ticket


@router.post("/{ticket_id}/reply", response_model=AdminTicketDetail, status_code=201)
def send_reply(ticket_id: int, body: ReplyCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    ticket = _get_ticket(db, ticket_id)
    add_admin_reply(db, admin, ticket, body)
    return _get_ticket(db, ticket_id)


@router.post("/{ticket_id}/notes", response_model=NoteOut, status_code=201)
def add_note(ticket_id: int, body: NoteCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    ticket = _get_ticket(db, ticket_id)
    note = InternalNote(ticket_id=ticket.id, admin_id=admin.id, body=body.body.strip())
    db.add(note)
    audit(db, ticket.id, admin.id, "note_added")
    db.commit()
    return note


@router.post("/{ticket_id}/draft/regenerate", response_model=AdminTicketDetail)
def regenerate_draft(ticket_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    ticket = _get_ticket(db, ticket_id)
    try:
        ticket.ai_draft = generate_draft(db, ticket)
        ticket.ai_draft_at = datetime.now(timezone.utc)
        ticket.ai_status = "ai_done"
        db.commit()
    except AIUnavailable:
        raise AppError(503, "ai_unavailable", "AI is not available right now. You can write the reply manually.")
    return ticket