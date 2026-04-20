from datetime import date as _date

from sqlalchemy.orm import Session

from app.core.errors import NotFound, ValidationFailed
from app.models.diary import Diary, DiaryStatus
from app.models.event import Event
from app.modules.registry import get_module
from app.repositories.diary_repo import DiaryRepository
from app.repositories.event_repo import EventRepository
from app.schemas.event import EventManualCreate, EventUpdate


class EventService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventRepository(db)
        self.diaries = DiaryRepository(db)

    def list_by_diary(self, diary_id: int) -> list[Event]:
        return self.events.list_by_diary(diary_id)

    def list_by_module(
        self, user_id: int, module_code: str, *, limit: int = 100, offset: int = 0
    ) -> list[Event]:
        return self.events.list_by_user_and_module(
            user_id, module_code, limit=limit, offset=offset
        )

    def create_manual(self, user_id: int, payload: EventManualCreate) -> Event:
        """Create an event NOT derived from a diary raw_text.

        Contract (ADR-007 · 2026-04-20): diary.raw_text is immutable. 用户手动
        补录 = 新建 event + locked=True；如果那天没有日记，自动建一个空壳
        Diary 作为外键归属，raw_text 置空。重解析时会跳过 locked 事件。
        """
        mod = get_module(payload.module_code)
        if mod is None:
            raise ValidationFailed(f"unknown module_code: {payload.module_code!r}")
        validated_data = mod.validate(payload.data)

        target_date = payload.date or _date.today()
        diary = self.diaries.get_by_user_and_date(user_id, target_date)
        if diary is None:
            diary = Diary(
                user_id=user_id,
                date=target_date,
                raw_text="",
                status=DiaryStatus.parsed,
            )
            self.diaries.add(diary)
            self.db.flush()

        event = Event(
            diary_id=diary.id,
            user_id=user_id,
            module_code=payload.module_code,
            raw_text=payload.raw_text or "",
            ai_processed_text=payload.ai_processed_text,
            data=validated_data,
            locked=True,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

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
