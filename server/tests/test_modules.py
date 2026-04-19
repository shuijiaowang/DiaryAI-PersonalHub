"""Smoke tests for the module registry: registration & schema generation."""
from app.modules.registry import all_codes, get_module, load_builtins


def setup_module(_module) -> None:
    load_builtins()


def test_builtin_modules_registered() -> None:
    codes = set(all_codes())
    assert {"weather", "meal", "expense", "memo"}.issubset(codes)


def test_each_module_has_schema_and_validator() -> None:
    for code in ("weather", "meal", "expense", "memo"):
        cls = get_module(code)
        assert cls is not None
        schema = cls.json_schema()
        assert isinstance(schema, dict)
        assert schema.get("type") == "object"


def test_memo_action_inserts_validate() -> None:
    cls = get_module("memo")
    assert cls is not None
    cls.validate({"content": "买抽纸", "done": False})
