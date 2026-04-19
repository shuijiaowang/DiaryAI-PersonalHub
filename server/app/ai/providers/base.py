"""LLM provider abstraction.

Hard rule (设计文档_ai.md §8.1): nothing in the codebase may import the openai
SDK or call an LLM HTTP API directly. All LLM access goes through this layer.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_in: int | None = None
    tokens_out: int | None = None
    latency_ms: int | None = None


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def chat(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse: ...
