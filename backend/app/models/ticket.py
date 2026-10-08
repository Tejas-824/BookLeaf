from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"
    # Speeds up the admin queue (filter + sort)
    __table_args__ = (Index("ix_tickets_queue", "status", "priority", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey("authors.author_id"), index=True)
    book_id: Mapped[str | None] = mapped_column(ForeignKey("books.book_id"), nullable=True)
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    attachment_name: Mapped[str | None] = mapped_column(String(255))  # UI only for now

    status: Mapped[str] = mapped_column(String(20), default="Open", index=True)

    # Final values (what the admin sees and can change)
    category: Mapped[str | None] = mapped_column(String(60), index=True)
    category_source: Mapped[str] = mapped_column(String(10), default="pending")  # pending|ai|rule|admin
    priority: Mapped[str] = mapped_column(String(10), default="Medium")
    priority_source: Mapped[str] = mapped_column(String(10), default="pending")

    # Original AI suggestion (never overwritten, used for accuracy stats)
    ai_category: Mapped[str | None] = mapped_column(String(60))
    ai_priority: Mapped[str | None] = mapped_column(String(10))
    ai_confidence: Mapped[str | None] = mapped_column(String(10))

    ai_status: Mapped[str] = mapped_column(String(12), default="ai_pending")  # ai_pending|ai_done|ai_failed
    ai_draft: Mapped[str | None] = mapped_column(Text)  # cached draft
    ai_draft_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(64), unique=True)  # stops double submit

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    author = relationship("Author")
    book = relationship("Book")
    messages = relationship(
        "TicketMessage", order_by="TicketMessage.id", cascade="all, delete-orphan"
    )
    notes = relationship("InternalNote", order_by="InternalNote.id", cascade="all, delete-orphan")

    @property
    def book_title(self) -> str | None:
        return self.book.title if self.book else None