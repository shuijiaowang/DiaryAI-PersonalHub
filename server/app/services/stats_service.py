"""Aggregation queries for the dashboard.

NOTE: implementations here are intentionally minimal — extend as new modules
gain importance. All queries scope by user_id.
"""
from datetime import date

from sqlalchemy import Numeric, func, select
from sqlalchemy.orm import Session

from app.models.event import Event


class StatsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def expense_by_day(
        self, user_id: int, start: date, end: date
    ) -> list[dict]:
        """Sum expense.price per day. Assumes module_code='expense' and data->>'price' numeric-castable."""
        price_expr = func.coalesce(
            func.cast(Event.data["价格"].astext, Numeric), 0
        )
        stmt = (
            select(
                func.date(Event.created_at).label("d"),
                func.sum(price_expr).label("total"),
            )
            .where(
                Event.user_id == user_id,
                Event.module_code == "expense",
                func.date(Event.created_at) >= start,
                func.date(Event.created_at) <= end,
            )
            .group_by("d")
            .order_by("d")
        )
        return [{"date": row.d.isoformat(), "total": float(row.total or 0)} for row in self.db.execute(stmt)]

    def event_count_by_module(self, user_id: int) -> list[dict]:
        stmt = (
            select(Event.module_code, func.count().label("n"))
            .where(Event.user_id == user_id)
            .group_by(Event.module_code)
            .order_by(func.count().desc())
        )
        return [{"module_code": row.module_code, "count": row.n} for row in self.db.execute(stmt)]
