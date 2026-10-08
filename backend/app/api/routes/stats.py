from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.db.session import get_db
from app.models.ai_log import AILog
from app.models.ticket import Ticket
from app.models.user import User

router = APIRouter(prefix="/api/admin/stats", tags=["Admin: Stats"])

# Approx Claude Haiku price per 1M tokens (USD). Update if pricing changes.
PRICE_IN, PRICE_OUT = 1.0, 5.0


@router.get("")
def ai_stats(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(Ticket.id)))
    by_status = dict(db.execute(select(Ticket.status, func.count()).group_by(Ticket.status)).all())

    ai_rated = db.scalar(select(func.count()).select_from(Ticket).where(Ticket.ai_category.is_not(None)))
    cat_ok = db.scalar(
        select(func.count()).select_from(Ticket).where(Ticket.ai_category.is_not(None), Ticket.category == Ticket.ai_category)
    )
    pri_ok = db.scalar(
        select(func.count()).select_from(Ticket).where(Ticket.ai_priority.is_not(None), Ticket.priority == Ticket.ai_priority)
    )

    calls, tin, tout, avg_ms, failed = db.execute(
        select(
            func.count(AILog.id),
            func.coalesce(func.sum(AILog.input_tokens), 0),
            func.coalesce(func.sum(AILog.output_tokens), 0),
            func.coalesce(func.avg(AILog.latency_ms), 0),
            func.coalesce(func.sum(case((AILog.success.is_(False), 1), else_=0)), 0),
        )
    ).one()

    pct = lambda a, b: round(100 * a / b, 1) if b else None
    return {
        "total_tickets": total,
        "tickets_by_status": by_status,
        "category_accepted_pct": pct(cat_ok, ai_rated),
        "priority_accepted_pct": pct(pri_ok, ai_rated),
        "ai_calls": calls,
        "ai_failed_calls": int(failed),
        "input_tokens": int(tin),
        "output_tokens": int(tout),
        "avg_latency_ms": int(avg_ms),
        "estimated_cost_usd": round(tin / 1e6 * PRICE_IN + tout / 1e6 * PRICE_OUT, 4),
    }