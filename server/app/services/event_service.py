from datetime import date as _date

from sqlalchemy.orm import Session

from app.core.errors import NotFound, ValidationFailed
from app.models.diary import Diary, DiaryStatus
from app.models.event import Event
from app.modules.registry import get_module
from app.repositories.diary_repo import DiaryRepository
from app.repositories.event_repo import EventRepository
from app.schemas.event import EventManualCreate, EventUpdate
from app.services.diary_revision_log import append_revision_log_entry, event_snapshot_text


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

        Current MVP contract: 用户图形化补录写 event（locked=True），并在
        diary.raw_text 末尾追加一条“系统修改记录”。
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
        diary.raw_text = append_revision_log_entry(
            diary.raw_text,
            f"新增事件（{payload.module_code}）"
            f"：{event_snapshot_text(module_code=payload.module_code, raw_text=payload.raw_text, data=validated_data)}",
        )
        self.db.commit()
        self.db.refresh(event)
        return event

    def update(self, user_id: int, event_id: int, payload: EventUpdate) -> Event:
        event = self.events.get(event_id)
        if not event or event.user_id != user_id:
            raise NotFound("event not found")
        before_text = event_snapshot_text(
            module_code=event.module_code,
            raw_text=event.raw_text,
            data=event.data,
        )
        changed = False
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(event, field, value)
            changed = True
        # User edit -> lock so AI cannot overwrite on re-parse.
        if any(
            getattr(payload, f) is not None for f in ("raw_text", "ai_processed_text", "data")
        ):
            event.locked = True
        if changed:
            diary = self.diaries.get(event.diary_id)
            if diary:
                after_text = event_snapshot_text(
                    module_code=event.module_code,
                    raw_text=event.raw_text,
                    data=event.data,
                )
                diary.raw_text = append_revision_log_entry(
                    diary.raw_text,
                    f"更新事件（{event.module_code}，ID={event.id}）：{before_text} -> {after_text}",
                )
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete(self, user_id: int, event_id: int) -> None:
        event = self.events.get(event_id)
        if not event or event.user_id != user_id:
            raise NotFound("event not found")
        diary = self.diaries.get(event.diary_id)
        if diary:
            snapshot = event_snapshot_text(
                module_code=event.module_code,
                raw_text=event.raw_text,
                data=event.data,
            )
            diary.raw_text = append_revision_log_entry(
                diary.raw_text,
                f"删除事件（{event.module_code}，ID={event.id}）：{snapshot}",
            )
        self.events.delete(event)
        self.db.commit()
