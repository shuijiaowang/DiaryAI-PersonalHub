from typing import Any

from pydantic import BaseModel, Field

from app.models.profile import Privacy
from app.schemas.common import TimestampedOut


class ProfileSectionUpsert(BaseModel):
    module_code: str
    content: dict[str, Any] = Field(default_factory=dict)
    privacy: Privacy = Privacy.ai_only


class ProfileSectionOut(TimestampedOut):
    user_id: int
    module_code: str
    content: dict[str, Any]
    privacy: Privacy
    updated_by_event_id: int | None
