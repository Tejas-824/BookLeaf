from fastapi import APIRouter, BackgroundTasks, Depends, Header, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import require_author
from app.core.errors import AppError
from app.db.session import get_db
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketOut
from app.services.ai_pipeline import run_pipeline
from app.services.ticket_service import create_ticket

router = APIRouter(prefix="/api/tickets", tags=["Author: Tickets"])


@router.post("", response_model=TicketOut, status_code=201)
def submit_ticket(
    body: TicketCreate,
    background: BackgroundTasks,
    response: Response,
    idempotency_key: str | None = Header(default=None, max_length=64),
    user: User = Depends(require_author),
    db: Session = Depends(get_db),
):
    ticket, created = create_ticket(db, user, body, idempotency_key)
    if created:
        background.add_task(run_pipeline, ticket.id)  # runs after the response is sent
    else:
        response.status_code = 200  # duplicate submit, return the existing ticket
    return ticket


@router.get("", response_model=list[TicketOut])
def my_tickets(user: User = Depends(require_author), db: Session = Depends(get_db)):
    stmt = (
        select(Ticket)
        .where(Ticket.author_id == user.author_id)
        .options(selectinload(Ticket.messages), selectinload(Ticket.book))
        .order_by(Ticket.updated_at.desc())
    )
    return db.scalars(stmt).all()


@router.get("/{ticket_id}", response_model=TicketOut)
def my_ticket(ticket_id: int, user: User = Depends(require_author), db: Session = Depends(get_db)):
    ticket = db.scalar(
        select(Ticket)
        .where(Ticket.id == ticket_id, Ticket.author_id == user.author_id)
        .options(selectinload(Ticket.messages), selectinload(Ticket.book))
    )
    if not ticket:  # 404 (not 403) so we don't reveal that the ticket exists
        raise AppError(404, "ticket_not_found", "Ticket not found.")
    return ticket