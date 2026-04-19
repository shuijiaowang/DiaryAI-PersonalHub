"""Memo module — the canonical example of a *stateful* module that uses ACTIONS.

Storage: we reuse the `event` table (each todo item is one event row whose
`data` carries `{content, due, done, done_at}`). Actions update those rows
instead of always inserting new ones.
"""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.errors import ValidationFailed
from app.models.event import Event
from app.modules._base import Module
from app.modules.registry import register
from app.schemas.ai import ParsedAction


class MemoData(BaseModel):
    content: str = Field(min_length=1)
    due: date | None = None
    done: bool = False
    done_at: date | None = None


@register
class MemoModule(Module):
    code = "memo"
    name = "备忘录"
    description = "从日记中识别待办事项；后续日记若提及完成，则自动标记完成。"
    actions = ["insert", "update"]
    prompt_fragment = (
        "维护一份待办列表。新出现的待办（如『明天要买抽纸』）→ 用 action=insert 添加；"
        "若日记提到某条已存在的待办已完成，并且你能从画像 / 数据库上下文里识别它的 id，"
        "→ 用 action=update + target_id + value={done: true, done_at: <日期>}。"
        "不要重复 insert 已存在的待办。"
    )
    DataSchema = MemoData

    @classmethod
    def apply_action(
        cls,
        db: Session,
        *,
        user_id: int,
        diary_id: int,
        action: ParsedAction,
    ) -> None:
        if action.action == "insert":
            data = cls.validate(action.value)
            row = Event(
                diary_id=diary_id,
                user_id=user_id,
                module_code=cls.code,
                raw_text=data["content"],
                ai_processed_text=data["content"],
                data=data,
                locked=False,
            )
            db.add(row)
            db.flush()
            return

        if action.action == "update":
            if not action.target_id:
                raise ValidationFailed("memo update requires target_id")
            row = db.get(Event, action.target_id)
            if row is None or row.user_id != user_id or row.module_code != cls.code:
                raise ValidationFailed(f"memo target_id {action.target_id} not found")
            merged = {**row.data, **action.value}
            row.data = cls.validate(merged)
            db.flush()
            return

        raise ValidationFailed(f"memo: unsupported action {action.action!r}")
