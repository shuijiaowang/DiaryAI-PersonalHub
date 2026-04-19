from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampedOut(ORMBase):
    id: int
    created_at: datetime
    updated_at: datetime


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int = 1
    size: int = 20


class Message(BaseModel):
    message: str
