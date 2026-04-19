"""DTOs for the AI pipeline I/O. These are also what each module's `schema()` should produce."""
from typing import Any, Literal

from pydantic import BaseModel, Field


class ParsedEvent(BaseModel):
    """A single event extracted from a diary by the LLM."""

    module_code: str
    raw_text: str
    ai_processed_text: str = ""
    data: dict[str, Any] = Field(default_factory=dict)


class ParsedAction(BaseModel):
    """An action the LLM wants the system to perform on a stateful module
    (e.g. memo: insert / update / delete).
    """

    module_code: str
    action: Literal["insert", "update", "delete", "append"]
    target_id: int | None = None
    value: dict[str, Any] = Field(default_factory=dict)


class DiaryParseResult(BaseModel):
    """Top-level structured output the LLM is asked to return for a diary."""

    ai_processed_text: str = ""
    events: list[ParsedEvent] = Field(default_factory=list)
    actions: list[ParsedAction] = Field(default_factory=list)
