from sqlalchemy.orm import Session

from app.ai.providers.base import LLMResponse
from app.models.ai_call_log import AICallLog, AICallStatus


def log_call(
    db: Session,
    *,
    user_id: int | None,
    diary_id: int | None,
    prompt_hash: str,
    prompt: str,
    response: LLMResponse | None,
    status: AICallStatus,
    error: str | None = None,
) -> AICallLog:
    row = AICallLog(
        user_id=user_id,
        diary_id=diary_id,
        provider=response.provider if response else "?",
        model=response.model if response else "?",
        prompt_hash=prompt_hash,
        prompt=prompt,
        response=response.content if response else None,
        tokens_in=response.tokens_in if response else None,
        tokens_out=response.tokens_out if response else None,
        latency_ms=response.latency_ms if response else None,
        status=status,
        error=error,
    )
    db.add(row)
    db.flush()
    return row
