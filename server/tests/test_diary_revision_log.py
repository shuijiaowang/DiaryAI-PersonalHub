from app.services.diary_revision_log import (
    REVISION_LOG_HEADER,
    append_revision_log_entry,
    split_raw_text_and_revision_log,
)


def test_append_revision_log_entry_creates_tail_block() -> None:
    raw = "今天早上吃了鸡蛋。"
    updated = append_revision_log_entry(raw, "新增事件（meal）：早上吃了1个煎鸡蛋")
    body, tail = split_raw_text_and_revision_log(updated)

    assert body == raw
    assert REVISION_LOG_HEADER in tail
    assert "新增事件（meal）" in tail


def test_split_raw_text_and_revision_log_without_block() -> None:
    body, tail = split_raw_text_and_revision_log("只有正文")
    assert body == "只有正文"
    assert tail == ""
