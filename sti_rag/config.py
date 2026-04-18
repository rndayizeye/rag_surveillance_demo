"""
sti_rag/config.py
-----------------
Layered configuration system for the STI Surveillance RAG assistant.

Load order (later layers override earlier ones):
  1. Defaults — sti_rag/config.yaml (committed to the repo)
  2. Environment variables — override any setting at deploy time

Design goals:
  - A single AppConfig dataclass is the only object the rest of the codebase
    imports. No scattered os.getenv() calls in engine.py or app.py.
  - All validation happens in one place, at startup, with clear error messages.
  - Testable: tests can construct AppConfig directly without touching env vars
    or the filesystem.
  - Zero magic: the load order and override rules are documented and explicit.

Usage
-----
    from sti_rag.config import get_config

    cfg = get_config()          # cached singleton — safe to call many times
    cfg.validate()              # raises ConfigurationError if anything is wrong
    print(cfg.data_dir)         # Path object, resolved to an absolute path
    print(cfg.system_prompt)    # str
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_PACKAGE_DIR = Path(__file__).parent          # .../sti_rag/
_REPO_ROOT = _PACKAGE_DIR.parent             # repo root
_DEFAULT_CONFIG_PATH = _PACKAGE_DIR / "config.yaml"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""


# ---------------------------------------------------------------------------
# AppConfig dataclass
# ---------------------------------------------------------------------------

@dataclass
class AppConfig:
    """
    Typed, validated configuration for the entire application.

    Construct via get_config() in production code.
    Construct directly in tests to avoid filesystem/env-var coupling.

    All Path fields are resolved to absolute paths relative to the repo root,
    so the app behaves identically whether launched from the repo root,
    from inside the sti_rag/ package dir, or from inside a Docker container.
    """

    # Secrets (must come from environment — never from config.yaml)
    pageindex_api_key: str = ""

    # Paths
    data_dir: Path = field(default_factory=lambda: _REPO_ROOT / "data")
    storage_dir: Path = field(default_factory=lambda: _REPO_ROOT / "storage")
    query_log: Path = field(default_factory=lambda: _REPO_ROOT / "query_logs.csv")

    # PageIndex polling
    poll_interval_seconds: int = 3
    poll_timeout_seconds: int = 300

    # UI copy
    page_title: str = "STI Surveillance AI"
    greeting: str = "Hello! Your surveillance manuals have been indexed. How can I assist?"

    # LLM
    system_prompt: str = (
        "You are an STI Surveillance Assistant for public health professionals. "
        "Answer questions strictly based on the uploaded manuals and memos. "
        "If the answer cannot be found in the provided documents, say so clearly "
        "and do not speculate. Always cite the section or page number when possible."
    )

    # ---------------------------------------------------------------------------
    # Derived paths (computed properties — not stored as fields)
    # ---------------------------------------------------------------------------

    @property
    def doc_registry(self) -> Path:
        """Path to the JSON file that maps PDF filenames to PageIndex doc IDs."""
        return self.storage_dir / "doc_registry.json"

    # ---------------------------------------------------------------------------
    # Validation
    # ---------------------------------------------------------------------------

    def validate(self) -> None:
        """
        Raise ConfigurationError with a complete list of all problems found.

        Call this once at application startup (app.py, before any widget renders).
        Collects all errors before raising so the user sees every problem at once,
        not just the first one encountered.
        """
        errors: list[str] = []

        # --- Required secrets ---
        if not self.pageindex_api_key:
            errors.append(
                "PAGEINDEX_API_KEY is not set. "
                "Get your key at https://dash.pageindex.ai/api-keys "
                "and add it to your .env file."
            )

        # --- Numeric bounds ---
        if self.poll_interval_seconds < 1:
            errors.append(
                f"poll_interval_seconds must be >= 1, got {self.poll_interval_seconds}."
            )
        if self.poll_timeout_seconds < 10:
            errors.append(
                f"poll_timeout_seconds must be >= 10, got {self.poll_timeout_seconds}."
            )
        if self.poll_timeout_seconds <= self.poll_interval_seconds:
            errors.append(
                "poll_timeout_seconds must be greater than poll_interval_seconds."
            )

        # --- Required strings ---
        if not self.system_prompt.strip():
            errors.append("system_prompt cannot be empty.")
        if not self.page_title.strip():
            errors.append("page_title cannot be empty.")

        if errors:
            bullet_list = "\n  - ".join(errors)
            raise ConfigurationError(
                f"Configuration is invalid. Fix the following and restart:\n  - {bullet_list}"
            )

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def ensure_dirs(self) -> None:
        """Create data and storage directories if they don't already exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def __repr__(self) -> str:
        # Never include the API key in repr output (appears in logs, tracebacks)
        key_hint = "***" if self.pageindex_api_key else "(not set)"
        return (
            f"AppConfig("
            f"pageindex_api_key={key_hint}, "
            f"data_dir={self.data_dir}, "
            f"poll_timeout_seconds={self.poll_timeout_seconds})"
        )


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def _load_yaml_defaults(path: Path) -> dict:
    """
    Load config.yaml. Returns an empty dict if the file is missing or
    unreadable — the dataclass defaults are the true baseline.
    """
    if not path.is_file():
        logger.warning("Config file not found at %s — using built-in defaults.", path)
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        logger.debug("Loaded config from %s", path)
        return data
    except yaml.YAMLError as exc:
        logger.warning("Could not parse %s (%s) — using built-in defaults.", path, exc)
        return {}


def _build_config(yaml_data: dict) -> AppConfig:
    """
    Merge yaml_data with environment variable overrides into an AppConfig.

    Override precedence (highest wins):
      env var  >  config.yaml value  >  AppConfig field default
    """

    def _path(yaml_section: str, yaml_key: str, env_var: str, default: Path) -> Path:
        raw = (
            os.environ.get(env_var)
            or yaml_data.get(yaml_section, {}).get(yaml_key)
        )
        p = Path(raw) if raw else default
        return p if p.is_absolute() else _REPO_ROOT / p

    def _int(yaml_section: str, yaml_key: str, env_var: str, default: int) -> int:
        raw = os.environ.get(env_var) or yaml_data.get(yaml_section, {}).get(yaml_key)
        if raw is None:
            return default
        try:
            return int(raw)
        except (TypeError, ValueError):
            logger.warning(
                "Invalid value for %s / %s.%s: %r — using default %d",
                env_var, yaml_section, yaml_key, raw, default,
            )
            return default

    def _str(yaml_section: str, yaml_key: str, env_var: str, default: str) -> str:
        # strip() removes trailing newlines that YAML block scalars (>) can add
        raw = os.environ.get(env_var) or yaml_data.get(yaml_section, {}).get(yaml_key)
        return str(raw).strip() if raw is not None else default

    return AppConfig(
        # Secrets — env var only, never from yaml
        pageindex_api_key=os.environ.get("PAGEINDEX_API_KEY", ""),

        # Paths
        data_dir=_path("paths", "data_dir", "STI_DATA_DIR", _REPO_ROOT / "data"),
        storage_dir=_path("paths", "storage_dir", "STI_STORAGE_DIR", _REPO_ROOT / "storage"),
        query_log=_path("paths", "query_log", "STI_QUERY_LOG", _REPO_ROOT / "query_logs.csv"),

        # PageIndex polling
        poll_interval_seconds=_int(
            "pageindex", "poll_interval_seconds", "STI_POLL_INTERVAL", 3
        ),
        poll_timeout_seconds=_int(
            "pageindex", "poll_timeout_seconds", "STI_POLL_TIMEOUT", 300
        ),

        # UI
        page_title=_str("ui", "page_title", "STI_PAGE_TITLE", "STI Surveillance AI"),
        greeting=_str("ui", "greeting", "STI_GREETING", "Hello! How can I assist?"),

        # LLM
        system_prompt=_str(
            "llm", "system_prompt", "STI_SYSTEM_PROMPT", AppConfig.system_prompt
        ),
    )


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """
    Return the application config singleton.

    The result is cached after the first call — all subsequent calls return
    the same object with zero overhead. In tests, call get_config.cache_clear()
    before each test that needs a fresh config.
    """
    yaml_data = _load_yaml_defaults(_DEFAULT_CONFIG_PATH)
    cfg = _build_config(yaml_data)
    logger.info("Configuration loaded: %r", cfg)
    return cfg
