"""Celery placeholder.

MVP uses FastAPI BackgroundTasks for diary parsing (good enough for single
user). When you outgrow it, swap `BackgroundTasks` calls in api/v1/diaries.py
with `parse_diary_task.delay(...)` defined here.
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "diaryai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
)


@celery_app.task(name="parse_diary")
def parse_diary_task(diary_id: int) -> dict:
    from app.tasks.parse_diary import run_parse_diary

    run_parse_diary(diary_id)
    return {"diary_id": diary_id, "status": "done"}
