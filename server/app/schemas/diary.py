from datetime import date

from pydantic import BaseModel, Field

from app.models.diary import DiaryStatus
from app.schemas.common import TimestampedOut
from app.schemas.event import EventOut


class DiaryCreate(BaseModel):
    date: date
    raw_text: str = Field(min_length=1)


class DiaryUpdate(BaseModel):
    raw_text: str | None = None


class DiaryOut(TimestampedOut):
    user_id: int
    date: date
    raw_text: str
    ai_processed_text: str | None
    status: DiaryStatus
    parse_error: str | None


class DiaryDetail(DiaryOut):
    events: list[EventOut] = []


class DiaryParseRequest(BaseModel):
    """Trigger (re)parsing of an existing diary."""

    force: bool = False
