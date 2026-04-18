"""
tests/test_engine.py
--------------------
Unit tests for sti_rag.engine.

The PageIndex API is mocked throughout — no network calls, no API key needed.
Run with:  pytest
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sti_rag.engine import PageIndexChatEngine, PageIndexResponse, _load_registry, _save_registry


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

def test_save_and_load_registry(tmp_path, monkeypatch):
    monkeypatch.setattr("sti_rag.config.STORAGE_DIR", tmp_path)
    monkeypatch.setattr("sti_rag.config.DOC_REGISTRY", tmp_path / "doc_registry.json")

    from sti_rag import config
    registry = {"manual_a.pdf": "pi-abc123", "manual_b.pdf": "pi-def456"}
    _save_registry(registry)
    assert _load_registry() == registry


def test_load_registry_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("sti_rag.config.DOC_REGISTRY", tmp_path / "nonexistent.json")
    assert _load_registry() == {}


def test_load_registry_corrupt_file(tmp_path, monkeypatch):
    bad = tmp_path / "doc_registry.json"
    bad.write_text("NOT JSON", encoding="utf-8")
    monkeypatch.setattr("sti_rag.config.DOC_REGISTRY", bad)
    assert _load_registry() == {}


# ---------------------------------------------------------------------------
# PageIndexChatEngine
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_client():
    client = MagicMock()
    client.chat_completions.return_value = {
        "choices": [{"message": {"content": "Chlamydia reporting threshold is 5 cases per 100k."}}]
    }
    return client


@pytest.fixture
def pdf_files(tmp_path):
    files = [tmp_path / "manual_a.pdf", tmp_path / "manual_b.pdf"]
    for f in files:
        f.write_bytes(b"%PDF-1.4 fake")
    return files


def test_chat_returns_response(mock_client, pdf_files):
    engine = PageIndexChatEngine(mock_client, ["pi-abc", "pi-def"], pdf_files)
    response = engine.chat("What is the reporting threshold for chlamydia?")
    assert isinstance(response, PageIndexResponse)
    assert "chlamydia" in response.response.lower()


def test_chat_builds_conversation_history(mock_client, pdf_files):
    engine = PageIndexChatEngine(mock_client, ["pi-abc"], pdf_files)
    engine.chat("First question")
    engine.chat("Second question")

    # Second call should include prior history
    second_call_messages = mock_client.chat_completions.call_args_list[1][1]["messages"]
    roles = [m["role"] for m in second_call_messages]
    assert roles == ["system", "user", "assistant", "user"]


def test_reset_clears_history(mock_client, pdf_files):
    engine = PageIndexChatEngine(mock_client, ["pi-abc"], pdf_files)
    engine.chat("A question")
    engine.reset()
    assert engine._history == []


def test_source_nodes_populated(mock_client, pdf_files):
    engine = PageIndexChatEngine(mock_client, ["pi-abc", "pi-def"], pdf_files)
    response = engine.chat("Any question")
    assert len(response.source_nodes) == len(pdf_files)
    assert response.source_nodes[0].metadata["file_name"] == pdf_files[0].name


def test_single_doc_passes_string_not_list(mock_client, pdf_files):
    """When there is only one document, doc_id must be a string, not a list."""
    engine = PageIndexChatEngine(mock_client, ["pi-only"], pdf_files[:1])
    engine.chat("Question")
    call_kwargs = mock_client.chat_completions.call_args[1]
    assert isinstance(call_kwargs["doc_id"], str)


def test_multi_doc_passes_list(mock_client, pdf_files):
    engine = PageIndexChatEngine(mock_client, ["pi-abc", "pi-def"], pdf_files)
    engine.chat("Question")
    call_kwargs = mock_client.chat_completions.call_args[1]
    assert isinstance(call_kwargs["doc_id"], list)
