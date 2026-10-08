from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import Category, Priority, Status
from app.schemas.book import BookOut
from app.schemas.ticket import MessageOut


class TicketUpdate(BaseModel):
    status: Status | None = None
    category: Category | None = None
    priority: Priority | None = None


class ReplyCreate(BaseModel):
    body: str = Field(min_length=5, max_length=5000)
    set_status: Status = "In Progress"  # status after replying


class NoteCreate(BaseModel):
    body: str = Field(min_length=1, max_length=3000)


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admin_id: int
    body: str
    created_at: datetime


class AuthorBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    author_id: str
    name: str
    email: str
    city: str | None


class AdminTicketDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    description: str
    attachment_name: str | None
    status: str
    category: str | None
    category_source: str
    priority: str
    priority_source: str
    ai_category: str | None
    ai_priority: str | None
    ai_confidence: str | None
    ai_status: str
    ai_draft: str | None
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime
    author: AuthorBrief
    book: BookOut | None
    messages: list[MessageOut]
    notes: list[NoteOut]