"""Redis-backed prompt cache.

Same prompt + same model => same answer (deterministic re-runs save tokens).
"""
import hashlib

import redis

from app.core.config import settings
from app.core.logging import logger

_client: redis.Redis | None = None


def _get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _client


def hash_prompt(provider: str, model: str, prompt: str) -> str:
    h = hashlib.sha256()
    h.update(provider.encode())
    h.update(b"|")
    h.update(model.encode())
    h.update(b"|")
    h.update(prompt.encode("utf-8"))
    return h.hexdigest()


def get(prompt_hash: str) -> str | None:
    if not settings.LLM_CACHE_ENABLED:
        return None
    try:
        return _get_client().get(f"llm:cache:{prompt_hash}")
    except redis.RedisError as e:
        logger.warning(f"redis get failed (cache miss treated): {e}")
        return None


def set(prompt_hash: str, content: str, ttl_seconds: int = 7 * 24 * 3600) -> None:
    if not settings.LLM_CACHE_ENABLED:
        return
    try:
        _get_client().setex(f"llm:cache:{prompt_hash}", ttl_seconds, content)
    except redis.RedisError as e:
        logger.warning(f"redis set failed (ignored): {e}")
