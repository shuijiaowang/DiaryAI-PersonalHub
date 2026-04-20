"""Aggregation queries for the dashboard.

NOTE: implementations here are intentionally minimal — extend as new modules
gain importance. All queries scope by user_id.
"""
from datetime import date
from typing import Literal

from sqlalchemy import Numeric, func, select
from sqlalchemy.orm import Session

from app.models.event import Event

Granularity = Literal["day", "week", "month", "year"]

_EXPENSE_PRICE = func.coalesce(func.cast(Event.data["价格"].astext, Numeric), 0)
_EXPENSE_CATEGORY = func.coalesce(Event.data["消费类型"].astext, "其他")


class StatsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---------------------------------------------------------------- expense

    def expense_by_period(
        self,
        user_id: int,
        start: date,
        end: date,
        granularity: Granularity = "day",
    ) -> list[dict]:
        """Sum expense.price grouped by day/week/month/year."""
        bucket = func.date_trunc(granularity, Event.created_at).label("bucket")
        stmt = (
            select(
                bucket,
                func.sum(_EXPENSE_PRICE).label("total"),
                func.count().label("count"),
            )
            .where(*self._expense_scope(user_id, start, end))
            .group_by(bucket)
            .order_by(bucket)
        )
        rows = self.db.execute(stmt).all()
        return [
            {
                "bucket": row.bucket.date().isoformat() if row.bucket else None,
                "total": float(row.total or 0),
                "count": int(row.count or 0),
            }
            for row in rows
        ]

    def expense_summary(self, user_id: int, start: date, end: date) -> dict:
        stmt = select(
            func.coalesce(func.sum(_EXPENSE_PRICE), 0).label("total"),
            func.count().label("count"),
            func.coalesce(func.avg(_EXPENSE_PRICE), 0).label("avg"),
            func.coalesce(func.max(_EXPENSE_PRICE), 0).label("max"),
        ).where(*self._expense_scope(user_id, start, end))
        row = self.db.execute(stmt).one()
        return {
            "total": float(row.total or 0),
            "count": int(row.count or 0),
            "avg": float(row.avg or 0),
            "max": float(row.max or 0),
            "start": start.isoformat(),
            "end": end.isoformat(),
        }

    def expense_by_category(
        self, user_id: int, start: date, end: date
    ) -> list[dict]:
        stmt = (
            select(
                _EXPENSE_CATEGORY.label("category"),
                func.sum(_EXPENSE_PRICE).label("total"),
                func.count().label("count"),
            )
            .where(*self._expense_scope(user_id, start, end))
            .group_by(_EXPENSE_CATEGORY)
            .order_by(func.sum(_EXPENSE_PRICE).desc())
        )
        return [
            {
                "category": row.category,
                "total": float(row.total or 0),
                "count": int(row.count or 0),
            }
            for row in self.db.execute(stmt)
        ]

    def expense_items(
        self,
        user_id: int,
        start: date,
        end: date,
        *,
        limit: int = 200,
        offset: int = 0,
    ) -> list[dict]:
        """Flat list of expense events in a range, newest first. Used by the stats table."""
        stmt = (
            select(Event)
            .where(*self._expense_scope(user_id, start, end))
            .order_by(Event.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = list(self.db.scalars(stmt))
        return [
            {
                "id": ev.id,
                "diary_id": ev.diary_id,
                "created_at": ev.created_at.isoformat(),
                "raw_text": ev.raw_text,
                "ai_processed_text": ev.ai_processed_text,
                "locked": ev.locked,
                "data": ev.data,
            }
            for ev in rows
        ]

    # ---------------------------------------------------------------- generic

    def event_count_by_module(self, user_id: int) -> list[dict]:
        stmt = (
            select(Event.module_code, func.count().label("n"))
            .where(Event.user_id == user_id)
            .group_by(Event.module_code)
            .order_by(func.count().desc())
        )
        return [{"module_code": row.module_code, "count": row.n} for row in self.db.execute(stmt)]

    # ------------------------------------------------------------- internals

    @staticmethod
    def _expense_scope(user_id: int, start: date, end: date):
        return (
            Event.user_id == user_id,
            Event.module_code == "expense",
            func.date(Event.created_at) >= start,
            func.date(Event.created_at) <= end,
        )

    # ---------------------------------------------------------------- legacy

    def expense_by_day(self, user_id: int, start: date, end: date) -> list[dict]:
        """Kept for backward compatibility with the old Dashboard card."""
        rows = self.expense_by_period(user_id, start, end, "day")
        return [{"date": r["bucket"], "total": r["total"]} for r in rows]
