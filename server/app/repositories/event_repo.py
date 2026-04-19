from sqlalchemy import delete, select

from app.models.event import Event
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    model = Event

    def list_by_diary(self, diary_id: int) -> list[Event]:
        return list(self.db.scalars(select(Event).where(Event.diary_id == diary_id)))

    def list_by_user_and_module(
        self, user_id: int, module_code: str, *, limit: int = 100, offset: int = 0
    ) -> list[Event]:
        stmt = (
            select(Event)
            .where(Event.user_id == user_id, Event.module_code == module_code)
            .order_by(Event.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt))

    def delete_unlocked_by_diary(self, diary_id: int) -> int:
        """Delete events of a diary that the user has NOT manually edited.

        Used when re-parsing a diary so we don't overwrite user corrections.
        """
        stmt = delete(Event).where(Event.diary_id == diary_id, Event.locked.is_(False))
        result = self.db.execute(stmt)
        return result.rowcount or 0
