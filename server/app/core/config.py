from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file.

    Hard rule (see 设计文档_ai.md §8): no secrets are allowed in source code.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_ENV: Literal["dev", "test", "prod"] = "dev"
    APP_DEBUG: bool = True
    APP_NAME: str = "DiaryAI-PersonalHub"
    APP_VERSION: str = "0.1.0"

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    # When True: allow any Origin (testing). Must use allow_credentials=False in Starlette.
    # When False: use CORS_ORIGINS + credentials (typical prod / fixed dev ports).
    CORS_ALLOW_ALL: bool = True
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    DATABASE_URL: str = "postgresql+psycopg://diary:diary@localhost:5432/diary"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MIN: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 14

    LLM_PROVIDER: Literal["deepseek", "openai", "ollama"] = "deepseek"
    LLM_MODEL: str = "deepseek-chat"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 4096
    LLM_TIMEOUT_S: int = 60
    # Set to false if you don't want to install Redis locally; cache becomes a no-op.
    LLM_CACHE_ENABLED: bool = True

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    OLLAMA_BASE_URL: str = "http://localhost:11434"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
