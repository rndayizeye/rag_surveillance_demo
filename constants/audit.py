"""
sti_rag/audit.py
----------------
Audit logging for all query/response pairs.

Kept in its own module so it can be tested independently, swapped for a
database-backed implementation later, or imported by other future modules
(e.g. an admin dashboard) without pulling in the full RAG engine.
"""

import csv
import logging
from datetime import datetime

from sti_rag.config import QUERY_LOG

logger = logging.getLogger(__name__)


def log_query(query: str, response_text: str, source_files: list[str]) -> None:
    """
    Append one row to the CSV audit log.

    Creates the file with a header row on first write.
    Failures are logged as warnings — a logging error should never crash
    the application or interrupt the user.

    Parameters
    ----------
    query:
        The raw question the user asked.
    response_text:
        The assistant's full answer (truncated to 300 chars in the log).
    source_files:
        List of PDF filenames that were searched to produce the answer.
    """
    file_exists = QUERY_LOG.is_file()
    try:
        with open(QUERY_LOG, "a", newline="", encoding="utf-8") as f:
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
        logger.warning("Could not write to audit log at %s: %s", QUERY_LOG, exc)
