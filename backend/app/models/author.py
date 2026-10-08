from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Author(Base):
    __tablename__ = "authors"

    author_id: Mapped[str] = mapped_column(String(10), primary_key=True)  # e.g. AUTH001
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    city: Mapped[str | None] = mapped_column(String(80))
    joined_date: Mapped[date | None] = mapped_column(Date)

    books = relationship("Book", back_populates="author")