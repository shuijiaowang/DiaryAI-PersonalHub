"""Base class every business module inherits from.

Module = schema (Pydantic) + prompt fragment + allowed actions + apply_action()

Hard rule (设计文档_ai.md §8.5): no `if module_code == "expense"` branches in
the main flow. Add behavior by subclassing and registering, never by editing
the executor.
"""
from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.errors import ValidationFailed
from app.schemas.ai import ParsedAction


class Module:
    code: ClassVar[str]                 # e.g. "expense"
    name: ClassVar[str]                 # human-readable Chinese name
    description: ClassVar[str] = ""
    prompt_fragment: ClassVar[str] = ""
    actions: ClassVar[list[str]] = []   # empty = pure event module
    DataSchema: ClassVar[type[BaseModel]]

    @classmethod
    def json_schema(cls) -> dict[str, Any]:
        return cls.DataSchema.model_json_schema()

    @classmethod
    def validate(cls, data: dict[str, Any]) -> dict[str, Any]:
        try:
            return cls.DataSchema.model_validate(data).model_dump()
        except Exception as e:
            raise ValidationFailed(f"[{cls.code}] data invalid: {e}") from e

    # default: pure event module, no actions
    @classmethod
    def apply_action(
        cls,
        db: Session,
        *,
        user_id: int,
        diary_id: int,
        action: ParsedAction,
    ) -> None:
        raise ValidationFailed(
            f"module '{cls.code}' does not support actions (got {action.action!r})"
        )
