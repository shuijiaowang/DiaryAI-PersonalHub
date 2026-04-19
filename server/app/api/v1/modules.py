from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.module import Module
from app.models.user import User
from app.schemas.module import ModuleOut, ModuleToggle
from app.services.module_service import ModuleService

router = APIRouter()


@router.get("", response_model=list[ModuleOut])
def list_modules(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Module]:
    return ModuleService(db).list_all()


@router.patch("/{code}", response_model=ModuleOut)
def toggle_module(
    code: str,
    payload: ModuleToggle,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Module:
    return ModuleService(db).set_enabled(code, payload.enabled)
