from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.profile import ProfileSection
from app.models.user import User
from app.schemas.profile import ProfileSectionOut, ProfileSectionUpsert
from app.services.profile_service import ProfileService

router = APIRouter()


@router.get("", response_model=list[ProfileSectionOut])
def list_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ProfileSection]:
    return ProfileService(db).list_for_user(user.id)


@router.put("", response_model=ProfileSectionOut)
def upsert_profile(
    payload: ProfileSectionUpsert,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProfileSection:
    return ProfileService(db).upsert(user.id, payload)
