import enum

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TimestampMixin


class Privacy(str, enum.Enum):
    public = "public"
    ai_only = "ai_only"
    private = "private"


class ProfileSection(Base, IdMixin, TimestampMixin):
    """One row per (user, module). Stores the user's global info per module."""

    __tablename__ = "profile_section"
    __table_args__ = (
        UniqueConstraint("user_id", "module_code", name="uq_profile_user_module"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    module_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    privacy: Mapped[Privacy] = mapped_column(
        Enum(Privacy, name="profile_privacy"),
        default=Privacy.ai_only,
        nullable=False,
    )

    updated_by_event_id: Mapped[int | None] = mapped_column(
        ForeignKey("event.id", ondelete="SET NULL"), nullable=True
    )
