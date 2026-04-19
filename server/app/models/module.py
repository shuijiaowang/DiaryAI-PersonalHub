from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TimestampMixin


class Module(Base, IdMixin, TimestampMixin):
    """Module registry table.

    Builtin modules also have a row here (synced on app startup) so that the
    frontend can list / enable / disable them uniformly with plugin modules.
    """

    __tablename__ = "module"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    schema: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    prompt_fragment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    actions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
