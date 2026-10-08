from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_author
from app.db.session import get_db
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookOut

router = APIRouter(prefix="/api/books", tags=["Author: Books"])


@router.get("", response_model=list[BookOut])
def my_books(user: User = Depends(require_author), db: Session = Depends(get_db)):
    # Filter by the logged-in author. An author can never see another author's books.
    return db.scalars(select(Book).where(Book.author_id == user.author_id).order_by(Book.book_id)).all()