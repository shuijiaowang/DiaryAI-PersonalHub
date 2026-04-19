from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.stats_service import StatsService

router = APIRouter()


@router.get("/expense/by-day")
def expense_by_day(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict]:
    if end is None:
        end = date.today()
    if start is None:
        start = end - timedelta(days=30)
    return StatsService(db).expense_by_day(user.id, start, end)


@router.get("/events/by-module")
def events_by_module(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict]:
    return StatsService(db).event_count_by_module(user.id)
