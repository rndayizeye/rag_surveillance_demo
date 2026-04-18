"""
sti_rag/audit.py
----------------
Audit logging for all query/response pairs.
"""

import csv
import logging
from datetime import datetime

from sti_rag.config import get_config

logger = logging.getLogger(__name__)


def log_query(query: str, response_text: str, source_files: list[str]) -> None:
    """
    Append one row to the CSV audit log.

    Creates the file with a header row on first write.
    Failures are logged as warnings and never crash the application.
    """
    cfg = get_config()
    file_exists = cfg.query_log.is_file()
    try:
        with open(cfg.query_log, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["timestamp", "query", "response_summary", "sources"],
            )
            if not file_exists:
                writer.writeheader()
            writer.writerow(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "query": query,
                    "response_summary": response_text[:300].replace("\n", " "),
                    "sources": "; ".join(source_files),
                }
            )
    except OSError as exc:
        logger.warning("Could not write to audit log at %s: %s", cfg.query_log, exc)
