import time

from openai import APIConnectionError, APIError, AuthenticationError, OpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.ai.providers.base import LLMProvider, LLMResponse
from app.core.config import settings
from app.core.errors import AIError


class DeepSeekProvider(LLMProvider):
    name = "deepseek"

    def __init__(self) -> None:
        if not settings.DEEPSEEK_API_KEY:
            raise AIError("DEEPSEEK_API_KEY is not configured")
        self._client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            timeout=settings.LLM_TIMEOUT_S,
        )

    @retry(
        reraise=True,
        retry=retry_if_exception_type((APIConnectionError, APIError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
    )
    def chat(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        t0 = time.perf_counter()
        try:
            resp = self._client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
                max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
            )
        except AuthenticationError as e:
            raise AIError(f"DeepSeek auth failed: {e}") from e
        latency_ms = int((time.perf_counter() - t0) * 1000)

        usage = getattr(resp, "usage", None)
        return LLMResponse(
            content=resp.choices[0].message.content or "",
            model=resp.model or settings.LLM_MODEL,
            provider=self.name,
            tokens_in=getattr(usage, "prompt_tokens", None) if usage else None,
            tokens_out=getattr(usage, "completion_tokens", None) if usage else None,
            latency_ms=latency_ms,
        )
