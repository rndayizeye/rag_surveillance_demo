"""
tests/test_config.py
--------------------
Tests for sti_rag.config — the layered configuration system.

Each test calls get_config.cache_clear() before running so it gets a fresh
config object unaffected by other tests or module-level imports.
"""

import os
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest

from sti_rag.config import (
    AppConfig,
    ConfigurationError,
    _build_config,
    _load_yaml_defaults,
    get_config,
)


@pytest.fixture(autouse=True)
def clear_config_cache():
    """Ensure every test starts with a clean config cache."""
    get_config.cache_clear()
    yield
    get_config.cache_clear()


# ---------------------------------------------------------------------------
# _load_yaml_defaults
# ---------------------------------------------------------------------------

def test_load_yaml_returns_empty_dict_for_missing_file(tmp_path):
    result = _load_yaml_defaults(tmp_path / "nonexistent.yaml")
    assert result == {}


def test_load_yaml_returns_empty_dict_for_corrupt_file(tmp_path):
    bad = tmp_path / "config.yaml"
    bad.write_text(": this is not valid yaml :", encoding="utf-8")
    result = _load_yaml_defaults(bad)
    assert result == {}


def test_load_yaml_parses_valid_file(tmp_path):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        dedent("""\
            pageindex:
              poll_interval_seconds: 10
              poll_timeout_seconds: 600
        """),
        encoding="utf-8",
    )
    result = _load_yaml_defaults(cfg_file)
    assert result["pageindex"]["poll_interval_seconds"] == 10
    assert result["pageindex"]["poll_timeout_seconds"] == 600


# ---------------------------------------------------------------------------
# _build_config — yaml values
# ---------------------------------------------------------------------------

def test_yaml_values_override_defaults():
    cfg = _build_config(
        {
            "pageindex": {"poll_interval_seconds": 10, "poll_timeout_seconds": 600},
            "ui": {"page_title": "Custom Title"},
            "llm": {"system_prompt": "Be concise."},
        }
    )
    assert cfg.poll_interval_seconds == 10
    assert cfg.poll_timeout_seconds == 600
    assert cfg.page_title == "Custom Title"
    assert cfg.system_prompt == "Be concise."


def test_invalid_int_yaml_value_falls_back_to_default():
    cfg = _build_config({"pageindex": {"poll_interval_seconds": "not-a-number"}})
    assert cfg.poll_interval_seconds == 3  # built-in default


# ---------------------------------------------------------------------------
# _build_config — env var overrides
# ---------------------------------------------------------------------------

def test_env_var_overrides_yaml(monkeypatch):
    monkeypatch.setenv("STI_POLL_TIMEOUT", "999")
    cfg = _build_config({"pageindex": {"poll_timeout_seconds": 300}})
    assert cfg.poll_timeout_seconds == 999


def test_env_var_overrides_system_prompt(monkeypatch):
    monkeypatch.setenv("STI_SYSTEM_PROMPT", "Custom prompt from env.")
    cfg = _build_config({})
    assert cfg.system_prompt == "Custom prompt from env."


def test_pageindex_api_key_comes_from_env_only(monkeypatch):
    monkeypatch.setenv("PAGEINDEX_API_KEY", "test-key-xyz")
    cfg = _build_config({})
    assert cfg.pageindex_api_key == "test-key-xyz"


def test_pageindex_api_key_empty_when_env_not_set(monkeypatch):
    monkeypatch.delenv("PAGEINDEX_API_KEY", raising=False)
    cfg = _build_config({})
    assert cfg.pageindex_api_key == ""


def test_relative_path_resolves_to_absolute(monkeypatch, tmp_path):
    monkeypatch.setenv("STI_DATA_DIR", "my_data")
    cfg = _build_config({})
    assert cfg.data_dir.is_absolute()


def test_absolute_path_used_as_is(monkeypatch, tmp_path):
    monkeypatch.setenv("STI_DATA_DIR", str(tmp_path / "custom_data"))
    cfg = _build_config({})
    assert cfg.data_dir == tmp_path / "custom_data"


# ---------------------------------------------------------------------------
# AppConfig.validate()
# ---------------------------------------------------------------------------

def test_validate_passes_with_valid_config():
    cfg = AppConfig(
        pageindex_api_key="valid-key",
        poll_interval_seconds=3,
        poll_timeout_seconds=300,
        system_prompt="You are helpful.",
        page_title="My App",
    )
    cfg.validate()  # should not raise


def test_validate_raises_for_missing_api_key():
    cfg = AppConfig(pageindex_api_key="")
    with pytest.raises(ConfigurationError, match="PAGEINDEX_API_KEY"):
        cfg.validate()


def test_validate_raises_for_empty_system_prompt():
    cfg = AppConfig(pageindex_api_key="key", system_prompt="   ")
    with pytest.raises(ConfigurationError, match="system_prompt"):
        cfg.validate()


def test_validate_raises_for_poll_interval_too_small():
    cfg = AppConfig(pageindex_api_key="key", poll_interval_seconds=0)
    with pytest.raises(ConfigurationError, match="poll_interval_seconds"):
        cfg.validate()


def test_validate_raises_for_timeout_not_greater_than_interval():
    cfg = AppConfig(
        pageindex_api_key="key",
        poll_interval_seconds=10,
        poll_timeout_seconds=5,
    )
    with pytest.raises(ConfigurationError, match="poll_timeout_seconds"):
        cfg.validate()


def test_validate_collects_multiple_errors():
    cfg = AppConfig(
        pageindex_api_key="",
        system_prompt="",
        page_title="",
    )
    with pytest.raises(ConfigurationError) as exc_info:
        cfg.validate()
    msg = str(exc_info.value)
    assert "PAGEINDEX_API_KEY" in msg
    assert "system_prompt" in msg
    assert "page_title" in msg


# ---------------------------------------------------------------------------
# AppConfig properties
# ---------------------------------------------------------------------------

def test_doc_registry_is_inside_storage_dir(tmp_path):
    cfg = AppConfig(storage_dir=tmp_path / "storage")
    assert cfg.doc_registry == tmp_path / "storage" / "doc_registry.json"


def test_repr_never_exposes_api_key():
    cfg = AppConfig(pageindex_api_key="super-secret-key-123")
    assert "super-secret-key-123" not in repr(cfg)
    assert "***" in repr(cfg)


def test_repr_shows_not_set_when_key_missing():
    cfg = AppConfig(pageindex_api_key="")
    assert "(not set)" in repr(cfg)


# ---------------------------------------------------------------------------
# get_config — singleton caching
# ---------------------------------------------------------------------------

def test_get_config_returns_same_instance(monkeypatch):
    monkeypatch.setenv("PAGEINDEX_API_KEY", "key")
    first = get_config()
    second = get_config()
    assert first is second


def test_get_config_cache_clear_produces_new_instance(monkeypatch):
    monkeypatch.setenv("PAGEINDEX_API_KEY", "key")
    first = get_config()
    get_config.cache_clear()
    second = get_config()
    assert first is not second


def test_get_config_reflects_env_change_after_cache_clear(monkeypatch):
    monkeypatch.setenv("STI_PAGE_TITLE", "First Title")
    assert get_config().page_title == "First Title"

    get_config.cache_clear()
    monkeypatch.setenv("STI_PAGE_TITLE", "Second Title")
    assert get_config().page_title == "Second Title"


# ---------------------------------------------------------------------------
# AppConfig.ensure_dirs
# ---------------------------------------------------------------------------

def test_ensure_dirs_creates_missing_directories(tmp_path):
    cfg = AppConfig(
        data_dir=tmp_path / "data",
        storage_dir=tmp_path / "storage",
    )
    assert not cfg.data_dir.exists()
    assert not cfg.storage_dir.exists()
    cfg.ensure_dirs()
    assert cfg.data_dir.is_dir()
    assert cfg.storage_dir.is_dir()


def test_ensure_dirs_is_idempotent(tmp_path):
    cfg = AppConfig(
        data_dir=tmp_path / "data",
        storage_dir=tmp_path / "storage",
    )
    cfg.ensure_dirs()
    cfg.ensure_dirs()  # should not raise
