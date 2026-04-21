from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

REVISION_LOG_HEADER = "【系统修改记录】"


def split_raw_text_and_revision_log(raw_text: str) -> tuple[str, str]:
    """Split diary raw text into body and tail revision-log block."""
    marker = raw_text.find(REVISION_LOG_HEADER)
    if marker == -1:
        return raw_text.strip(), ""
    body = raw_text[:marker].rstrip()
    tail = raw_text[marker:].strip()
    return body, tail


def append_revision_log_entry(raw_text: str, entry: str) -> str:
    body, tail = split_raw_text_and_revision_log(raw_text)
    line = f"- [{_now_label()}] {entry.strip()}"
    if tail:
        return f"{body}\n\n{tail}\n{line}".strip()
    return f"{body}\n\n{REVISION_LOG_HEADER}\n{line}".strip()


def event_snapshot_text(*, module_code: str, raw_text: str | None, data: dict[str, Any]) -> str:
    text = (raw_text or "").strip()
    if text:
        return f"{module_code}：{text}"
    return f"{module_code}：{json.dumps(data, ensure_ascii=False, sort_keys=True)}"


def _now_label() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
