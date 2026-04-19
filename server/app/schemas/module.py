from typing import Any

from pydantic import BaseModel

from app.schemas.common import TimestampedOut


class ModuleOut(TimestampedOut):
    code: str
    name: str
    description: str | None
    schema: dict[str, Any]
    prompt_fragment: str
    actions: list[str]
    is_builtin: bool
    enabled: bool


class ModuleToggle(BaseModel):
    enabled: bool
