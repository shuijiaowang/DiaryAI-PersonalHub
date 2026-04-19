from datetime import date

from sqlalchemy import select

from app.models.diary import Diary
from app.repositories.base import BaseRepository


class DiaryRepository(BaseRepository[Diary]):
    model = Diary

    def get_by_user_and_date(self, user_id: int, d: date) -> Diary | None:
        return self.db.scalar(
            select(Diary).where(Diary.user_id == user_id, Diary.date == d)
        )

    def list_by_user(self, user_id: int, *, limit: int = 50, offset: int = 0) -> list[Diary]:
        stmt = (
            select(Diary)
            .where(Diary.user_id == user_id)
            .order_by(Diary.date.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt))
