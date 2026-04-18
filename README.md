---
title: RAG Surveillance Pro
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8501
---

# STI Surveillance RAG Assistant

A professional RAG (Retrieval-Augmented Generation) assistant for public health professionals navigating STI surveillance manuals, CDC guidelines, and regional health memos.

Built with [PageIndex](https://github.com/VectifyAI/PageIndex) — a vectorless, reasoning-based retrieval framework that builds a hierarchical tree index from your documents and uses LLM reasoning to find relevant sections, rather than approximate vector similarity search.

## Features

- **Reasoning-based retrieval** — no vector database, no chunking artefacts. PageIndex navigates document structure the way a human analyst would.
- **Multi-document support** — upload several manuals at once; the engine queries across all of them.
- **Persistent indexing** — uploaded documents are indexed once and reused across sessions. Re-uploading the same file does not trigger re-indexing.
- **Audit trail** — every query and response is logged to a downloadable CSV for compliance review.
- **Containerised** — ships as a single Docker image for deployment on internal health department servers or Hugging Face Spaces.

## Project structure

```
rag_surveillance_demo/
├── sti_rag/                  # Application package
│   ├── __init__.py
│   ├── config.py             # Layered config (YAML defaults + env overrides)
│   ├── config.yaml           # Human-readable defaults — safe to commit
│   ├── engine.py             # PageIndex orchestration
│   └── audit.py              # CSV audit logging
├── tests/
│   ├── test_config.py
│   └── test_engine.py
├── data/                     # Uploaded PDFs (git-ignored)
├── storage/                  # Persisted PageIndex doc registry (git-ignored)
├── app.py                    # Streamlit UI
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Tech stack

| Layer | Technology |
|---|---|
| Retrieval | [PageIndex](https://github.com/VectifyAI/PageIndex) — vectorless, reasoning-based RAG |
| UI | [Streamlit](https://streamlit.io) |
| Container | Docker (multi-stage, non-root) |
| Deployment | Hugging Face Spaces |

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/rndayizeye/rag_surveillance_demo.git
cd rag_surveillance_demo
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and add your [PageIndex API key](https://dash.pageindex.ai/api-keys):

```
PAGEINDEX_API_KEY=your_key_here
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

Open [http://localhost:8501](http://localhost:8501).

### 4. Run locally without Docker

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### 5. Run tests

```bash
pip install pytest pytest-mock
pytest
```

## Configuration

All settings live in `sti_rag/config.yaml`. Every value can be overridden at deploy time with an environment variable — no code changes needed.

| Setting | YAML key | Env var | Default |
|---|---|---|---|
| PageIndex API key | — (secrets only) | `PAGEINDEX_API_KEY` | *(required)* |
| Data directory | `paths.data_dir` | `STI_DATA_DIR` | `data/` |
| Storage directory | `paths.storage_dir` | `STI_STORAGE_DIR` | `storage/` |
| Poll interval | `pageindex.poll_interval_seconds` | `STI_POLL_INTERVAL` | `3` |
| Poll timeout | `pageindex.poll_timeout_seconds` | `STI_POLL_TIMEOUT` | `300` |
| System prompt | `llm.system_prompt` | `STI_SYSTEM_PROMPT` | See config.yaml |

## Privacy & security

- **Zero-footprint** — uploaded documents are processed within the container and are never used to train global AI models.
- **Non-root container** — the Docker image runs as UID 1000 (`appuser`), not root.
- **Secrets management** — API keys are loaded from environment variables and are never committed to the repository.
- **Audit logging** — all queries and retrieved sources are written to `query_logs.csv`, downloadable from the sidebar.

## Live demo

**Hugging Face Space:** [rndayizeye-rag-surveillance-demo.hf.space](https://rndayizeye-rag-surveillance-demo.hf.space)

## Author

Public Health Professional | Regional Program Coordinator
Specialising in infectious disease surveillance and data analytics.
