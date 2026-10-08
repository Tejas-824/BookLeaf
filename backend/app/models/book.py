from datetime import date

from sqlalchemy import JSON, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Book(Base):
    __tablename__ = "books"

    book_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey("authors.author_id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    isbn: Mapped[str] = mapped_column(String(30))  # text, not number
    genre: Mapped[str | None] = mapped_column(String(100))
    publication_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(60))
    mrp: Mapped[int | None] = mapped_column(Integer)
    author_royalty_per_copy: Mapped[int | None] = mapped_column(Integer)
    total_copies_sold: Mapped[int] = mapped_column(Integer, default=0)
    total_royalty_earned: Mapped[int] = mapped_column(Integer, default=0)
    royalty_paid: Mapped[int] = mapped_column(Integer, default=0)
    royalty_pending: Mapped[int] = mapped_column(Integer, default=0)
    last_royalty_payout_date: Mapped[date | None] = mapped_column(Date)
    print_partner: Mapped[str | None] = mapped_column(String(60))
    available_on: Mapped[list] = mapped_column(JSON, default=list)

    author = relationship("Author", back_populates="books")