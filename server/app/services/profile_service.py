from sqlalchemy.orm import Session

from app.models.profile import ProfileSection
from app.repositories.profile_repo import ProfileRepository
from app.schemas.profile import ProfileSectionUpsert


class ProfileService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.profiles = ProfileRepository(db)

    def list_for_user(self, user_id: int) -> list[ProfileSection]:
        return self.profiles.list_by_user(user_id)

    def upsert(self, user_id: int, payload: ProfileSectionUpsert) -> ProfileSection:
        section = self.profiles.get(user_id, payload.module_code)
        if section is None:
            section = ProfileSection(
                user_id=user_id,
                module_code=payload.module_code,
                content=payload.content,
                privacy=payload.privacy,
            )
            self.profiles.add(section)
        else:
            section.content = payload.content
            section.privacy = payload.privacy
        self.db.commit()
        self.db.refresh(section)
        return section

    def collect_ai_context(self, user_id: int) -> dict[str, dict]:
        """Return a dict suitable for embedding into the LLM prompt."""
        return {
            s.module_code: s.content for s in self.profiles.list_for_ai_context(user_id)
        }
