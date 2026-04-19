"""Shared pytest fixtures.

Default: real LLM calls are mocked. End-to-end tests that require a real key
should live under tests/e2e_with_real_llm/ and be opt-in via env / marker.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_diary_text() -> str:
    return (FIXTURES_DIR / "diary_2026_3_5.txt").read_text(encoding="utf-8")
