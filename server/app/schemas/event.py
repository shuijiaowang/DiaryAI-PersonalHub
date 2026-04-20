from datetime import date as date_type
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedOut


class EventCreate(BaseModel):
    diary_id: int
    module_code: str
    raw_text: str
    ai_processed_text: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class EventManualCreate(BaseModel):
    """User-authored event not derived from diary parsing (ADR-007)."""

    module_code: str
    data: dict[str, Any] = Field(default_factory=dict)
    date: date_type | None = Field(default=None, description="归属日期；默认为今天")
    raw_text: str | None = None
    ai_processed_text: str | None = None


class EventUpdate(BaseModel):
    raw_text: str | None = None
    ai_processed_text: str | None = None
    data: dict[str, Any] | None = None
    locked: bool | None = None


class EventOut(TimestampedOut):
    diary_id: int
    user_id: int
    module_code: str
    raw_text: str
    ai_processed_text: str | None
    data: dict[str, Any]
    locked: bool
