"""Module registry.

`register()` decorator collects modules. `sync_to_db()` writes builtin modules
into the `module` table on app startup so they become listable / toggleable.
"""
from __future__ import annotations

import json
from typing import Iterable

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.module import Module as ModuleRow
from app.modules._base import Module
from app.repositories.module_repo import ModuleRepository

_REGISTRY: dict[str, type[Module]] = {}


def register(cls: type[Module]) -> type[Module]:
    if not getattr(cls, "code", None):
        raise ValueError(f"module {cls} missing `code`")
    if cls.code in _REGISTRY:
        raise ValueError(f"duplicate module code: {cls.code}")
    _REGISTRY[cls.code] = cls
    return cls


def get_module(code: str) -> type[Module] | None:
    return _REGISTRY.get(code)


def iter_modules(*, enabled_only: bool = False) -> Iterable[type[Module]]:
    # NOTE: `enabled_only` checks runtime DB state via sync_to_db; here we just
    # return everything registered. The pipeline filters by DB enabled flag.
    yield from _REGISTRY.values()


def all_codes() -> list[str]:
    return list(_REGISTRY.keys())


def sync_to_db(db: Session) -> None:
    """Upsert each builtin module row. Existing rows keep their `enabled` flag."""
    repo = ModuleRepository(db)
    for cls in _REGISTRY.values():
        existing = repo.get_by_code(cls.code)
        schema = cls.json_schema()
        if existing is None:
            row = ModuleRow(
                code=cls.code,
                name=cls.name,
                description=cls.description,
                schema=schema,
                prompt_fragment=cls.prompt_fragment,
                actions=list(cls.actions),
                is_builtin=True,
                enabled=True,
            )
            db.add(row)
            logger.info(f"[modules] registered builtin: {cls.code}")
        else:
            existing.name = cls.name
            existing.description = cls.description
            existing.schema = schema
            existing.prompt_fragment = cls.prompt_fragment
            existing.actions = list(cls.actions)
            existing.is_builtin = True
    db.commit()
    logger.info(
        f"[modules] sync done. registered codes: {json.dumps(all_codes(), ensure_ascii=False)}"
    )


# Trigger registration of all builtin modules.
# Imports at the bottom to avoid circular issues.
def load_builtins() -> None:
    from app.modules import expense, meal, memo, weather  # noqa: F401
