from sqlalchemy import select

from app.models.module import Module
from app.repositories.base import BaseRepository


class ModuleRepository(BaseRepository[Module]):
    model = Module

    def get_by_code(self, code: str) -> Module | None:
        return self.db.scalar(select(Module).where(Module.code == code))

    def list_enabled(self) -> list[Module]:
        return list(self.db.scalars(select(Module).where(Module.enabled.is_(True))))

    def list_all(self) -> list[Module]:
        return list(self.db.scalars(select(Module).order_by(Module.code)))
