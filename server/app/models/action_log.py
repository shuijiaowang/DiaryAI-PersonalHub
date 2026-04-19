import enum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TimestampMixin


class ActionStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    rolled_back = "rolled_back"


class ActionLog(Base, IdMixin, TimestampMixin):
    """Audit + rollback support for AI-emitted actions (insert / update / delete ...)."""

    __tablename__ = "action_log"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    diary_id: Mapped[int | None] = mapped_column(
        ForeignKey("diary.id", ondelete="SET NULL"), nullable=True, index=True
    )
    module_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus, name="action_status"), default=ActionStatus.success, nullable=False
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
