## 🤖 Model Attribution & Development

This project relies on the following models for its RAG (Retrieval-Augmented Generation) pipeline. Contributors should ensure any updates remain compatible with these specific versions:

### Inference Engine
- **LLM:** `Llama-3.1-8b-instant` via **Groq**. 
- **Purpose:** Contextual reasoning and response generation.
- **Documentation:** [Groq Cloud Console](https://console.groq.com/)

### Semantic Search
- **Embeddings:** `BAAI/bge-small-en-v1.5` via **Hugging Face**.
- **Purpose:** Vectorization of surveillance manuals for similarity search.
- **Reference:** [BGE Embedding Series](https://huggingface.co/BAAI/bge-small-en-v1.5)

### Development Guidelines
- If proposing a new LLM, please verify that it supports `condense_plus_context` chat modes within the LlamaIndex framework.
- Any changes to the embedding model will require a full re-indexing of the `storage/` directory.