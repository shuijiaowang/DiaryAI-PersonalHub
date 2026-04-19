from sqlalchemy.orm import Session

from app.core.errors import NotFound
from app.models.module import Module
from app.repositories.module_repo import ModuleRepository


class ModuleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.modules = ModuleRepository(db)

    def list_all(self) -> list[Module]:
        return self.modules.list_all()

    def list_enabled(self) -> list[Module]:
        return self.modules.list_enabled()

    def get(self, code: str) -> Module:
        m = self.modules.get_by_code(code)
        if not m:
            raise NotFound(f"module not found: {code}")
        return m

    def set_enabled(self, code: str, enabled: bool) -> Module:
        m = self.get(code)
        m.enabled = enabled
        self.db.commit()
        self.db.refresh(m)
        return m
