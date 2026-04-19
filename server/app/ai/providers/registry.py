from functools import lru_cache

from app.ai.providers.base import LLMProvider
from app.core.config import settings
from app.core.errors import AIError


@lru_cache(maxsize=4)
def get_provider(name: str | None = None) -> LLMProvider:
    name = (name or settings.LLM_PROVIDER).lower()
    if name == "deepseek":
        from app.ai.providers.deepseek import DeepSeekProvider

        return DeepSeekProvider()
    if name == "openai":
        from app.ai.providers.openai_provider import OpenAIProvider

        return OpenAIProvider()
    # Future: ollama, anthropic, ...
    raise AIError(f"unsupported LLM provider: {name}")
