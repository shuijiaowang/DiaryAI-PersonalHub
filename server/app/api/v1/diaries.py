from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.diary import Diary, DiaryStatus
from app.models.user import User
from app.schemas.common import Message
from app.schemas.diary import (
    DiaryCreate,
    DiaryDetail,
    DiaryOut,
    DiaryParseRequest,
    DiaryUpdate,
)
from app.services.diary_service import DiaryService
from app.services.event_service import EventService
from app.tasks.parse_diary import run_parse_diary

router = APIRouter()


@router.post("", response_model=DiaryOut, status_code=201)
def create_diary(
    payload: DiaryCreate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Diary:
    diary = DiaryService(db).create(user.id, payload)
    # MVP: trigger parsing in background tasks. Swap with Celery later.
    background.add_task(run_parse_diary, diary.id)
    return diary


@router.get("", response_model=list[DiaryOut])
def list_diaries(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Diary]:
    return DiaryService(db).list_for_user(user.id, limit=limit, offset=offset)


@router.get("/{diary_id}", response_model=DiaryDetail)
def get_diary(
    diary_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DiaryDetail:
    diary = DiaryService(db).get_owned(user.id, diary_id)
    events = EventService(db).list_by_diary(diary.id)
    detail = DiaryDetail.model_validate(diary)
    detail.events = [e for e in events]  # type: ignore[assignment]
    return detail


@router.patch("/{diary_id}", response_model=DiaryOut)
def update_diary(
    diary_id: int,
    payload: DiaryUpdate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Diary:
    diary = DiaryService(db).update(user.id, diary_id, payload)
    if diary.status == DiaryStatus.draft:
        background.add_task(run_parse_diary, diary.id)
    return diary


@router.delete("/{diary_id}", response_model=Message)
def delete_diary(
    diary_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Message:
    DiaryService(db).delete(user.id, diary_id)
    return Message(message="deleted")


@router.post("/{diary_id}/parse", response_model=Message)
def parse_diary(
    diary_id: int,
    payload: DiaryParseRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Message:
    diary = DiaryService(db).get_owned(user.id, diary_id)
    background.add_task(run_parse_diary, diary.id)
    return Message(message=f"parsing scheduled for diary {diary.id}")
