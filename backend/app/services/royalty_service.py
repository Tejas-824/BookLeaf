from datetime import date, timedelta

from app.core.constants import MIN_PAYOUT
from app.models.author import Author
from app.models.book import Book


def next_payout_date(today: date | None = None) -> date:
    """Payout is due 45 days after a quarter ends. Return the next such date."""
    today = today or date.today()
    for year in (today.year - 1, today.year, today.year + 1):
        for month, day in ((3, 31), (6, 30), (9, 30), (12, 31)):
            due = date(year, month, day) + timedelta(days=45)
            if due >= today:
                return due
    raise RuntimeError("unreachable")


def _months_since(d: date, today: date) -> int:
    return (today.year - d.year) * 12 + (today.month - d.month)


def _book_lines(b: Book, today: date) -> list[str]:
    lines = [f"Title: {b.title} (ISBN {b.isbn}, {b.genre})", f"Status: {b.status}"]

    if b.publication_date is None:  # book still in production
        lines.append("Not published yet, so there are no sales or royalty for this book.")
        return lines

    lines += [
        f"Published: {b.publication_date} ({_months_since(b.publication_date, today)} months ago)",
        f"MRP: Rs. {b.mrp}",
        f"Copies sold: {b.total_copies_sold}",
        f"Royalty earned: Rs. {b.total_royalty_earned}, paid: Rs. {b.royalty_paid}, pending: Rs. {b.royalty_pending}",
        f"Last payout date: {b.last_royalty_payout_date or 'never paid'}",
        f"Print partner: {b.print_partner}",
        f"Available on: {', '.join(b.available_on) or 'none'}",
    ]
    if 0 < b.royalty_pending < MIN_PAYOUT:
        lines.append(f"Pending amount is below the Rs. {MIN_PAYOUT} minimum, so it rolls over to the next quarter.")
    if b.total_royalty_earned > 0 and b.royalty_paid == 0:
        lines.append("No royalty has ever been paid for this book.")
    return lines


def build_facts_text(author: Author, book: Book | None, today: date | None = None) -> str:
    """Short, factual text about this author only. Nothing from other authors."""
    today = today or date.today()
    out = [
        f"Author: {author.name} (first name: {author.name.split()[0]})",
        f"Today: {today}",
        f"Next quarterly payout date (calculated): {next_payout_date(today)}",
        "Bank details linked: unknown (not available in the system)",
    ]
    if book:
        out.append("Book this ticket is about:")
        out += ["- " + line for line in _book_lines(book, today)]
    else:
        out.append("General / account-level ticket. Author's books (summary):")
        for b in author.books[:10]:
            out.append(f"- {b.title}: {b.status}, royalty pending Rs. {b.royalty_pending}")
    return "\n".join(out)