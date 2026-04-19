import enum
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TimestampMixin


class DiaryStatus(str, enum.Enum):
    draft = "draft"
    parsing = "parsing"
    parsed = "parsed"
    failed = "failed"


class Diary(Base, IdMixin, TimestampMixin):
    __tablename__ = "diary"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_diary_user_date"),)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    ai_processed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[DiaryStatus] = mapped_column(
        Enum(DiaryStatus, name="diary_status"),
        default=DiaryStatus.draft,
        nullable=False,
        index=True,
    )
    parse_error: Mapped[str | None] = mapped_column(Text, nullable=True)
