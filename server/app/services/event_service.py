from sqlalchemy.orm import Session

from app.core.errors import NotFound
from app.models.event import Event
from app.repositories.event_repo import EventRepository
from app.schemas.event import EventUpdate


class EventService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventRepository(db)

    def list_by_diary(self, diary_id: int) -> list[Event]:
        return self.events.list_by_diary(diary_id)

    def list_by_module(
        self, user_id: int, module_code: str, *, limit: int = 100, offset: int = 0
    ) -> list[Event]:
        return self.events.list_by_user_and_module(
            user_id, module_code, limit=limit, offset=offset
        )

    def update(self, user_id: int, event_id: int, payload: EventUpdate) -> Event:
        event = self.events.get(event_id)
        if not event or event.user_id != user_id:
            raise NotFound("event not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(event, field, value)
        # User edit -> lock so AI cannot overwrite on re-parse.
        if any(
            getattr(payload, f) is not None for f in ("raw_text", "ai_processed_text", "data")
        ):
            event.locked = True
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete(self, user_id: int, event_id: int) -> None:
        event = self.events.get(event_id)
        if not event or event.user_id != user_id:
            raise NotFound("event not found")
        self.events.delete(event)
        self.db.commit()
