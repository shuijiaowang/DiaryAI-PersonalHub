"""Apply ParsedEvents + ParsedActions atomically to the DB.

Contract:
  - All work happens inside a single transaction.
  - Each individual action also writes a row to action_log.
  - On any failure: full rollback + diary marked as failed; exception propagates.
"""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.core.errors import AIError
from app.core.logging import logger
from app.models.action_log import ActionLog, ActionStatus
from app.models.diary import Diary, DiaryStatus
from app.models.event import Event
from app.modules.registry import get_module
from app.repositories.event_repo import EventRepository
from app.schemas.ai import DiaryParseResult, ParsedAction, ParsedEvent


class ActionExecutor:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventRepository(db)

    def apply(self, diary: Diary, result: DiaryParseResult) -> None:
        try:
            self._apply_inner(diary, result)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            diary.status = DiaryStatus.failed
            diary.parse_error = f"action_executor: {e}"
            self.db.commit()
            raise

    def _apply_inner(self, diary: Diary, result: DiaryParseResult) -> None:
        # 1. Update diary's processed text + clear unlocked events for re-parse.
        diary.ai_processed_text = result.ai_processed_text or diary.ai_processed_text
        locked_signatures = {
            self._event_signature(ev.module_code, ev.data)
            for ev in self.events.list_locked_by_diary(diary.id)
        }
        deleted = self.events.delete_unlocked_by_diary(diary.id)
        if deleted:
            logger.info(f"[executor] cleared {deleted} unlocked events of diary={diary.id}")

        # 2. Create events.
        for ev in result.events:
            self._insert_event(diary, ev, locked_signatures)

        # 3. Apply actions (memo etc.).
        for act in result.actions:
            self._apply_action(diary, act)

        diary.status = DiaryStatus.parsed
        diary.parse_error = None

    def _insert_event(
        self, diary: Diary, ev: ParsedEvent, locked_signatures: set[tuple[str, str]]
    ) -> None:
        mod = get_module(ev.module_code)
        if mod is None:
            raise AIError(f"unknown module_code from LLM: {ev.module_code!r}")
        validated = mod.validate(ev.data)  # raises if invalid
        signature = self._event_signature(ev.module_code, validated)
        if signature in locked_signatures:
            logger.info(
                f"[executor] skip duplicate parsed event matched locked event: "
                f"diary={diary.id} module={ev.module_code}"
            )
            return
        row = Event(
            diary_id=diary.id,
            user_id=diary.user_id,
            module_code=ev.module_code,
            raw_text=ev.raw_text,
            ai_processed_text=ev.ai_processed_text,
            data=validated,
        )
        self.db.add(row)
        self.db.flush()

    def _apply_action(self, diary: Diary, act: ParsedAction) -> None:
        mod = get_module(act.module_code)
        if mod is None:
            raise AIError(f"unknown module_code in action: {act.module_code!r}")
        log = ActionLog(
            user_id=diary.user_id,
            diary_id=diary.id,
            module_code=act.module_code,
            action=act.action,
            payload=act.value,
            status=ActionStatus.success,
        )
        try:
            mod.apply_action(
                self.db, user_id=diary.user_id, diary_id=diary.id, action=act
            )
        except Exception as e:
            log.status = ActionStatus.failed
            log.error = str(e)
            self.db.add(log)
            self.db.flush()
            raise
        self.db.add(log)
        self.db.flush()

    @staticmethod
    def _event_signature(module_code: str, data: dict) -> tuple[str, str]:
        return module_code, json.dumps(data, ensure_ascii=False, sort_keys=True)
