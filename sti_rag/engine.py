"""
sti_rag/engine.py
-----------------
PageIndex-powered RAG engine — pure orchestration logic.

All configuration is read from get_config().
All audit logging is delegated to sti_rag.audit.
"""

import json
import logging
import time
from pathlib import Path

from pageindex import PageIndexClient

from sti_rag.audit import log_query
from sti_rag.config import get_config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Document registry helpers
# ---------------------------------------------------------------------------

def _load_registry() -> dict[str, str]:
    """Return {filename: pageindex_doc_id} from the persisted JSON file."""
    registry_path = get_config().doc_registry
    if registry_path.is_file():
        try:
            return json.loads(registry_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_registry(registry: dict[str, str]) -> None:
    cfg = get_config()
    cfg.storage_dir.mkdir(parents=True, exist_ok=True)
    cfg.doc_registry.write_text(json.dumps(registry, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Engine factory
# ---------------------------------------------------------------------------

def get_rag_engine(data_path: Path | None = None) -> "PageIndexChatEngine":
    """
    Build (or reload) the PageIndex chat engine.

    Raises
    ------
    FileNotFoundError  — data directory has no PDFs.
    RuntimeError       — a document failed processing or timed out.
    """
    cfg = get_config()
    data_path = data_path or cfg.data_dir

    pdf_files = sorted(
        f for f in data_path.iterdir()
        if f.is_file() and not f.name.startswith(".") and f.suffix.lower() == ".pdf"
    ) if data_path.is_dir() else []

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF documents found. Please upload files via the sidebar."
        )

    pi_client = PageIndexClient(api_key=cfg.pageindex_api_key)

    registry = _load_registry()
    pending: dict[str, str] = {}

    for pdf in pdf_files:
        if pdf.name not in registry:
            logger.info("Submitting '%s' to PageIndex …", pdf.name)
            result = pi_client.submit_document(str(pdf))
            pending[pdf.name] = result["doc_id"]

    if pending:
        _poll_until_ready(pi_client, pending, registry)
        _save_registry(registry)

    current_doc_ids = [registry[f.name] for f in pdf_files if f.name in registry]
    return PageIndexChatEngine(pi_client, current_doc_ids, pdf_files)


def _poll_until_ready(
    client: PageIndexClient,
    pending: dict[str, str],
    registry: dict[str, str],
) -> None:
    """Block until all pending documents are processed. Mutates registry in place."""
    cfg = get_config()
    deadline = time.monotonic() + cfg.poll_timeout_seconds
    remaining = dict(pending)

    while remaining:
        if time.monotonic() > deadline:
            raise RuntimeError(
                f"PageIndex processing timed out for: {list(remaining.keys())}. "
                "Try again in a few minutes."
            )
        time.sleep(cfg.poll_interval_seconds)
        for fname in list(remaining.keys()):
            doc_id = remaining[fname]
            status = client.get_document(doc_id).get("status", "")
            if status == "completed":
                logger.info("  ✓ '%s' ready (doc_id=%s)", fname, doc_id)
                registry[fname] = doc_id
                del remaining[fname]
            elif status == "failed":
                raise RuntimeError(
                    f"PageIndex failed to process '{fname}'. "
                    "Ensure the file is a valid, non-encrypted PDF."
                )


# ---------------------------------------------------------------------------
# Chat engine
# ---------------------------------------------------------------------------

class PageIndexChatEngine:
    """
    Wraps the PageIndex Chat API with a stable .chat() interface.
    Sends full conversation history with every request (API is stateless).
    """

    def __init__(
        self,
        client: PageIndexClient,
        doc_ids: list[str],
        pdf_files: list[Path],
    ) -> None:
        self._client = client
        self._doc_ids = doc_ids
        self._pdf_files = pdf_files
        self._history: list[dict] = []

    def chat(self, message: str) -> "PageIndexResponse":
        cfg = get_config()
        messages = (
            [{"role": "system", "content": cfg.system_prompt}]
            + self._history
            + [{"role": "user", "content": message}]
        )

        raw = self._client.chat_completions(
            messages=messages,
            doc_id=self._doc_ids if len(self._doc_ids) > 1 else self._doc_ids[0],
        )
        answer = raw["choices"][0]["message"]["content"]

        self._history.append({"role": "user", "content": message})
        self._history.append({"role": "assistant", "content": answer})

        source_names = [p.name for p in self._pdf_files]
        log_query(message, answer, source_names)

        return PageIndexResponse(answer, source_names)

    def reset(self) -> None:
        self._history = []


# ---------------------------------------------------------------------------
# Response object
# ---------------------------------------------------------------------------

class PageIndexResponse:
    def __init__(self, answer: str, source_file_names: list[str]) -> None:
        self.response = answer
        self.source_nodes = [_SourceNode(name) for name in source_file_names]


class _SourceNode:
    def __init__(self, file_name: str) -> None:
        self.metadata = {"file_name": file_name}

    def get_text(self) -> str:
        return "(See answer above for inline page and section citations.)"
