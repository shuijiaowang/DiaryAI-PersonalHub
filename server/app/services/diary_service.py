from sqlalchemy.orm import Session

from app.core.errors import Conflict, NotFound
from app.models.diary import Diary, DiaryStatus
from app.repositories.diary_repo import DiaryRepository
from app.repositories.event_repo import EventRepository
from app.schemas.diary import DiaryCreate, DiaryUpdate


class DiaryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.diaries = DiaryRepository(db)
        self.events = EventRepository(db)

    def create(self, user_id: int, payload: DiaryCreate) -> Diary:
        existing = self.diaries.get_by_user_and_date(user_id, payload.date)
        if existing:
            raise Conflict("diary for this date already exists; use update instead")
        diary = Diary(
            user_id=user_id,
            date=payload.date,
            raw_text=payload.raw_text,
            status=DiaryStatus.draft,
        )
        self.diaries.add(diary)
        self.db.commit()
        self.db.refresh(diary)
        return diary

    def get_owned(self, user_id: int, diary_id: int) -> Diary:
        diary = self.diaries.get(diary_id)
        if not diary or diary.user_id != user_id:
            raise NotFound("diary not found")
        return diary

    def list_for_user(self, user_id: int, *, limit: int = 50, offset: int = 0) -> list[Diary]:
        return self.diaries.list_by_user(user_id, limit=limit, offset=offset)

    def update(self, user_id: int, diary_id: int, payload: DiaryUpdate) -> Diary:
        diary = self.get_owned(user_id, diary_id)
        if payload.raw_text is not None:
            diary.raw_text = payload.raw_text
            diary.status = DiaryStatus.draft  # needs reparse
            diary.parse_error = None
        self.db.commit()
        self.db.refresh(diary)
        return diary

    def delete(self, user_id: int, diary_id: int) -> None:
        diary = self.get_owned(user_id, diary_id)
        self.diaries.delete(diary)
        self.db.commit()
