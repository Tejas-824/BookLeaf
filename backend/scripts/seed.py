import json
import sys
from datetime import date
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # so "app" can be imported

import app.models  # noqa: E402,F401
from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.models.author import Author  # noqa: E402
from app.models.book import Book  # noqa: E402
from app.models.user import User  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data" / "bookleaf_sample_data.json"
AUTHOR_PASSWORD = "Author@123"
ADMIN_EMAIL, ADMIN_PASSWORD = "admin@bookleaf.com", "Admin@123"


def d(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def main():
    Base.metadata.create_all(engine)
    data = json.loads(DATA.read_text(encoding="utf-8"))
    db = SessionLocal()
    pw_hash = hash_password(AUTHOR_PASSWORD)  # hash once, reuse (bcrypt is slow)

    for a in data["authors"]:
        if db.get(Author, a["author_id"]):
            continue  # already seeded
        db.add(
            Author(
                author_id=a["author_id"], name=a["name"], email=a["email"],
                phone=a["phone"], city=a["city"], joined_date=d(a["joined_date"]),
            )
        )
        db.flush()
        db.add(User(email=a["email"].lower(), password_hash=pw_hash, name=a["name"],
                    role="author", author_id=a["author_id"]))

        for b in a["books"]:
            # data sanity check: earned - paid should equal pending
            if b["total_royalty_earned"] - b["royalty_paid"] != b["royalty_pending"]:
                print(f"WARNING: royalty mismatch in {b['book_id']}")
            db.add(
                Book(
                    book_id=b["book_id"], author_id=a["author_id"], title=b["title"], isbn=b["isbn"],
                    genre=b["genre"], publication_date=d(b["publication_date"]), status=b["status"],
                    mrp=b["mrp"], author_royalty_per_copy=b["author_royalty_per_copy"],
                    total_copies_sold=b["total_copies_sold"], total_royalty_earned=b["total_royalty_earned"],
                    royalty_paid=b["royalty_paid"], royalty_pending=b["royalty_pending"],
                    last_royalty_payout_date=d(b["last_royalty_payout_date"]),
                    print_partner=b["print_partner"], available_on=b["available_on"],
                )
            )

    from sqlalchemy import select
    if not db.scalar(select(User).where(User.email == ADMIN_EMAIL)):
        db.add(User(email=ADMIN_EMAIL, password_hash=hash_password(ADMIN_PASSWORD), name="BookLeaf Admin", role="admin"))

    db.commit()
    db.close()
    print("Seed done. Author password:", AUTHOR_PASSWORD, "| Admin:", ADMIN_EMAIL, "/", ADMIN_PASSWORD)


if __name__ == "__main__":
    main()