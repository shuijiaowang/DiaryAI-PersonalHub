"""Diary -> structured (events + actions) pipeline.

Contract enforced here (设计文档_ai.md §4.1, §8):
  1. Always go through LLMProvider abstraction.
  2. Always log every LLM call to ai_call_log.
  3. Always validate LLM output against Pydantic schemas before it touches the DB.
  4. On schema failure, retry up to N times feeding the error back to the LLM.
"""
from __future__ import annotations

import json

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai import audit, cache
from app.ai.prompts import render
from app.ai.providers import get_provider
from app.ai.providers.base import LLMResponse
from app.core.config import settings
from app.core.errors import AIError
from app.core.logging import logger
from app.models.ai_call_log import AICallStatus
from app.modules.registry import get_module
from app.repositories.module_repo import ModuleRepository
from app.schemas.ai import DiaryParseResult
from app.services.profile_service import ProfileService

MAX_RETRIES = 3


class DiaryParserPipeline:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.provider = get_provider()

    def run(self, *, user_id: int, diary_id: int, diary_raw_text: str) -> DiaryParseResult:
        prompt = self._build_prompt(user_id=user_id, diary_raw_text=diary_raw_text)
        prompt_hash = cache.hash_prompt(self.provider.name, settings.LLM_MODEL, prompt)

        cached = cache.get(prompt_hash)
        if cached:
            logger.info(f"[diary_parser] cache hit hash={prompt_hash[:8]}")
            try:
                return DiaryParseResult.model_validate_json(cached)
            except ValidationError:
                logger.warning("[diary_parser] cache content invalid, falling through")

        last_error: str | None = None
        attempt_prompt = prompt
        for attempt in range(1, MAX_RETRIES + 1):
            response = self._call_llm(
                user_id=user_id, diary_id=diary_id, prompt=attempt_prompt, prompt_hash=prompt_hash
            )
            try:
                result = self._parse_and_validate(response.content)
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = str(e)
                logger.warning(
                    f"[diary_parser] attempt {attempt}/{MAX_RETRIES} validation failed: {e}"
                )
                attempt_prompt = self._build_retry_prompt(prompt, response.content, last_error)
                continue
            cache.set(prompt_hash, result.model_dump_json())
            return result

        raise AIError(f"diary parsing failed after {MAX_RETRIES} attempts: {last_error}")

    # ------------------------------------------------------------------ helpers

    def _build_prompt(self, *, user_id: int, diary_raw_text: str) -> str:
        global_info = ProfileService(self.db).collect_ai_context(user_id)
        modules = []
        for row in ModuleRepository(self.db).list_enabled():
            cls = get_module(row.code)
            if cls is None:
                logger.warning(f"[diary_parser] enabled module {row.code} has no python class; skipping")
                continue
            modules.append(
                {
                    "code": cls.code,
                    "name": cls.name,
                    "prompt_fragment": cls.prompt_fragment,
                    "schema_json": json.dumps(cls.json_schema(), ensure_ascii=False, indent=2),
                    "actions": cls.actions,
                }
            )
        return render(
            "diary_parser.j2",
            global_info_json=json.dumps(global_info, ensure_ascii=False, indent=2),
            modules=modules,
            diary_raw_text=diary_raw_text,
        )

    @staticmethod
    def _build_retry_prompt(original_prompt: str, bad_response: str, error: str) -> str:
        return (
            f"{original_prompt}\n\n"
            "## 上次返回的内容（不合法）\n"
            f"```\n{bad_response}\n```\n\n"
            "## 校验失败原因\n"
            f"{error}\n\n"
            "请严格按照上方「输出要求」重新输出，仅返回一个合法 JSON 对象。"
        )

    def _call_llm(
        self, *, user_id: int, diary_id: int, prompt: str, prompt_hash: str
    ) -> LLMResponse:
        try:
            resp = self.provider.chat(prompt)
        except Exception as e:
            audit.log_call(
                self.db,
                user_id=user_id,
                diary_id=diary_id,
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=None,
                status=AICallStatus.api_error,
                error=str(e),
            )
            self.db.commit()
            raise AIError(f"LLM call failed: {e}") from e

        audit.log_call(
            self.db,
            user_id=user_id,
            diary_id=diary_id,
            prompt_hash=prompt_hash,
            prompt=prompt,
            response=resp,
            status=AICallStatus.success,
        )
        self.db.commit()
        return resp

    @staticmethod
    def _parse_and_validate(content: str) -> DiaryParseResult:
        cleaned = _strip_code_fences(content)
        data = json.loads(cleaned)
        return DiaryParseResult.model_validate(data)


def _strip_code_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        # remove first fence (```json or ```)
        first_nl = s.find("\n")
        s = s[first_nl + 1 :] if first_nl != -1 else s[3:]
        if s.endswith("```"):
            s = s[:-3]
    return s.strip()
