from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TimestampMixin


class Event(Base, IdMixin, TimestampMixin):
    __tablename__ = "event"

    diary_id: Mapped[int] = mapped_column(
        ForeignKey("diary.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    module_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    ai_processed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
