import sys

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """Configure loguru as the only logger."""
    logger.remove()
    level = "DEBUG" if settings.APP_DEBUG else "INFO"
    logger.add(
        sys.stdout,
        level=level,
        backtrace=settings.APP_DEBUG,
        diagnose=settings.APP_DEBUG,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
            "| <level>{level: <8}</level> "
            "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>"
        ),
    )
    logger.add(
        "logs/app.log",
        rotation="20 MB",
        retention="14 days",
        level="INFO",
        enqueue=True,
        encoding="utf-8",
    )


__all__ = ["logger", "setup_logging"]
