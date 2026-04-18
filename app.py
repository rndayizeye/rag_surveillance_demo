"""
app.py — Streamlit UI for the STI Surveillance RAG assistant.
Contains no business logic — all config comes from sti_rag.config.
"""

import shutil

import streamlit as st
from dotenv import load_dotenv

from sti_rag import get_rag_engine
from sti_rag.config import ConfigurationError, get_config

# Load .env before anything else so env vars are available to get_config()
load_dotenv()

# ---------------------------------------------------------------------------
# Startup — validate config before rendering a single widget
# ---------------------------------------------------------------------------

try:
    cfg = get_config()
    cfg.validate()
    cfg.ensure_dirs()
except ConfigurationError as exc:
    st.error(str(exc))
    st.stop()

# ---------------------------------------------------------------------------
# Page config (values come from config, not hardcoded)
# ---------------------------------------------------------------------------

st.set_page_config(page_title=cfg.page_title, layout="wide")
st.title(f"🔍 {cfg.page_title}")

# ---------------------------------------------------------------------------
# Sidebar — Document Management
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("📂 Document Management")
    st.info(
        "Upload internal manuals, CDC guidelines, or memos. "
        "Documents are indexed using reasoning-based tree search — "
        "no vector database required."
    )

    uploaded_files = st.file_uploader(
        "Upload PDF Manuals",
        type="pdf",
        accept_multiple_files=True,
    )

    if st.button("🚀 Process Documents"):
        if uploaded_files:
            with st.spinner("Saving files and submitting to PageIndex…"):
                for uploaded_file in uploaded_files:
                    (cfg.data_dir / uploaded_file.name).write_bytes(
                        uploaded_file.getbuffer()
                    )
                st.session_state.pop("chat_engine", None)
                st.session_state.pop("messages", None)
            st.success("Files saved! The index will update on next load.")
            st.rerun()
        else:
            st.error("Please select at least one PDF file first.")

    if cfg.query_log.is_file():
        with open(cfg.query_log, "rb") as f:
            st.download_button("📥 Download Audit Log", f, "audit_log.csv", "text/csv")

    if st.button("🧹 Clear All Data"):
        for f in cfg.data_dir.iterdir():
            if not f.name.startswith("."):
                f.unlink()
        # Clear storage contents but not the directory itself — the directory
        # may be owned by root when mounted as a Docker volume, so rmtree
        # raises PermissionError. Deleting files inside it always works.
        if cfg.storage_dir.exists():
            for f in cfg.storage_dir.iterdir():
                if f.is_file():
                    f.unlink()
                elif f.is_dir():
                    shutil.rmtree(f)
        st.session_state.pop("chat_engine", None)
        st.session_state.pop("messages", None)
        st.rerun()

# ---------------------------------------------------------------------------
# Main UI — Chat Interface
# ---------------------------------------------------------------------------

real_files = [f for f in cfg.data_dir.iterdir() if not f.name.startswith(".")]

if not real_files:
    st.warning("⚠️ No documents found in the system.")
    st.markdown(
        """
### How to get started:
1. Open the **sidebar** on the left.
2. Upload one or more **STI Surveillance manuals** (PDF).
3. Click **Process Documents**.

*Documents are indexed by PageIndex into a reasoning-based tree structure.
Your files are not used to train any AI models.*
"""
    )
else:
    if "chat_engine" not in st.session_state:
        try:
            with st.spinner(
                "Building hierarchical tree index with PageIndex… "
                "This may take a moment for large documents."
            ):
                st.session_state.chat_engine = get_rag_engine()
        except FileNotFoundError as exc:
            st.error(str(exc))
            st.stop()
        except RuntimeError as exc:
            st.error(f"Document processing error: {exc}")
            st.stop()
        except Exception as exc:
            st.error(f"Unexpected error initialising engine: {exc}")
            st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": cfg.greeting}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about STI protocols…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_container = st.empty()
            with st.spinner("Reasoning through document tree…"):
                try:
                    response = st.session_state.chat_engine.chat(prompt)
                except Exception as exc:
                    st.error(f"Error querying the engine: {exc}")
                    st.stop()

            if hasattr(response, "source_nodes") and response.source_nodes:
                with st.expander("📝 Source Documents"):
                    for node in response.source_nodes:
                        st.write(f"**Source:** {node.metadata.get('file_name', 'Unknown')}")
                        st.caption(node.get_text())

            response_container.markdown(response.response)

        st.session_state.messages.append(
            {"role": "assistant", "content": response.response}
        )
