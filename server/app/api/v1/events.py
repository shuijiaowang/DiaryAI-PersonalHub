from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.event import Event
from app.models.user import User
from app.schemas.common import Message
from app.schemas.event import EventManualCreate, EventOut, EventUpdate
from app.services.event_service import EventService

router = APIRouter()


@router.post("", response_model=EventOut, status_code=201)
def create_manual_event(
    payload: EventManualCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Event:
    """手动补录一条事件（不修改日记原文，自动 locked=true）。见 ADR-007。"""
    return EventService(db).create_manual(user.id, payload)


@router.get("", response_model=list[EventOut])
def list_events(
    module_code: str = Query(..., min_length=1),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Event]:
    return EventService(db).list_by_module(user.id, module_code, limit=limit, offset=offset)


@router.patch("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Event:
    return EventService(db).update(user.id, event_id, payload)


@router.delete("/{event_id}", response_model=Message)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Message:
    EventService(db).delete(user.id, event_id)
    return Message(message="deleted")
