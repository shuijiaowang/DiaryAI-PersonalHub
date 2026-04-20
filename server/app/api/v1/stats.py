from datetime import date, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.stats_service import StatsService

router = APIRouter()

Granularity = Literal["day", "week", "month", "year"]


def _default_range(
    start: date | None, end: date | None, *, days: int = 30
) -> tuple[date, date]:
    if end is None:
        end = date.today()
    if start is None:
        start = end - timedelta(days=days)
    return start, end


@router.get("/expense/by-day")
def expense_by_day(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict]:
    """Legacy endpoint (kept for the old Dashboard card)."""
    start, end = _default_range(start, end)
    return StatsService(db).expense_by_day(user.id, start, end)


@router.get("/expense/by-period")
def expense_by_period(
    granularity: Granularity = Query(default="day"),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict]:
    start, end = _default_range(start, end, days=_default_days(granularity))
    return StatsService(db).expense_by_period(user.id, start, end, granularity)


@router.get("/expense/summary")
def expense_summary(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    start, end = _default_range(start, end)
    return StatsService(db).expense_summary(user.id, start, end)


@router.get("/expense/by-category")
def expense_by_category(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict]:
    start, end = _default_range(start, end)
    return StatsService(db).expense_by_category(user.id, start, end)


@router.get("/expense/items")
def expense_items(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict]:
    start, end = _default_range(start, end)
    return StatsService(db).expense_items(
        user.id, start, end, limit=limit, offset=offset
    )


@router.get("/events/by-module")
def events_by_module(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict]:
    return StatsService(db).event_count_by_module(user.id)


def _default_days(granularity: Granularity) -> int:
    return {"day": 30, "week": 90, "month": 365, "year": 365 * 5}[granularity]
