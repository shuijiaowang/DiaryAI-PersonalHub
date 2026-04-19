from sqlalchemy import select

from app.models.profile import Privacy, ProfileSection
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[ProfileSection]):
    model = ProfileSection

    def list_by_user(self, user_id: int) -> list[ProfileSection]:
        return list(
            self.db.scalars(select(ProfileSection).where(ProfileSection.user_id == user_id))
        )

    def list_for_ai_context(self, user_id: int) -> list[ProfileSection]:
        """Return only sections whose privacy allows feeding into an LLM."""
        return list(
            self.db.scalars(
                select(ProfileSection).where(
                    ProfileSection.user_id == user_id,
                    ProfileSection.privacy != Privacy.private,
                )
            )
        )

    def get(self, user_id: int, module_code: str) -> ProfileSection | None:  # type: ignore[override]
        return self.db.scalar(
            select(ProfileSection).where(
                ProfileSection.user_id == user_id,
                ProfileSection.module_code == module_code,
            )
        )
