"""End-to-end diary parsing entrypoint.

Same function is called both by FastAPI BackgroundTasks (sync version) and the
Celery task wrapper (see celery_app.py).
"""
from app.ai.pipelines.action_executor import ActionExecutor
from app.ai.pipelines.diary_parser import DiaryParserPipeline
from app.core.errors import DomainError
from app.core.logging import logger
from app.db.session import SessionLocal
from app.models.diary import Diary, DiaryStatus


def run_parse_diary(diary_id: int) -> None:
    db = SessionLocal()
    try:
        diary = db.get(Diary, diary_id)
        if diary is None:
            logger.warning(f"[parse_diary] diary {diary_id} not found, skipping")
            return

        diary.status = DiaryStatus.parsing
        diary.parse_error = None
        db.commit()

        try:
            pipeline = DiaryParserPipeline(db)
            result = pipeline.run(
                user_id=diary.user_id,
                diary_id=diary.id,
                diary_raw_text=diary.raw_text,
            )
            ActionExecutor(db).apply(diary, result)
            logger.info(f"[parse_diary] diary {diary_id} parsed: {len(result.events)} events, {len(result.actions)} actions")
        except DomainError as e:
            db.rollback()
            db.refresh(diary)
            diary.status = DiaryStatus.failed
            diary.parse_error = e.message
            db.commit()
            logger.error(f"[parse_diary] diary {diary_id} failed: {e.message}")
        except Exception as e:  # noqa: BLE001
            db.rollback()
            db.refresh(diary)
            diary.status = DiaryStatus.failed
            diary.parse_error = f"unexpected: {e!r}"
            db.commit()
            logger.exception(f"[parse_diary] diary {diary_id} unexpected failure")
    finally:
        db.close()
