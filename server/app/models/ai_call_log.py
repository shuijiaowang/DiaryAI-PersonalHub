import enum

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TimestampMixin


class AICallStatus(str, enum.Enum):
    success = "success"
    parse_failed = "parse_failed"
    api_error = "api_error"


class AICallLog(Base, IdMixin, TimestampMixin):
    __tablename__ = "ai_call_log"

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True
    )
    diary_id: Mapped[int | None] = mapped_column(
        ForeignKey("diary.id", ondelete="SET NULL"), nullable=True, index=True
    )

    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)

    prompt_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str | None] = mapped_column(Text, nullable=True)

    tokens_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_out: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost: Mapped[str | None] = mapped_column(String(32), nullable=True)

    status: Mapped[AICallStatus] = mapped_column(
        Enum(AICallStatus, name="ai_call_status"), default=AICallStatus.success, nullable=False
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
