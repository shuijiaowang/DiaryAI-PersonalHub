from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.db.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Thin base. Each repo holds the session and the model class.

    Hard rule: only data access lives here. No business logic.
    """

    model: type[T]

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, id_: int) -> T | None:
        return self.db.get(self.model, id_)

    def add(self, obj: T) -> T:
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, obj: T) -> None:
        self.db.delete(obj)
        self.db.flush()
