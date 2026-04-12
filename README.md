---
title: RAG Surveillance Demo
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.43.0"
python_version: "3.11"
app_file: app.py
pinned: false
---

# STI Surveillance Retrieval Augmented Generation (RAG)

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

## App screenshot 

![App Screenshot](https://private-user-images.githubusercontent.com/66800883/576983211-d5d9ba26-18e0-43b1-871a-c2225ac4dcac.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzU5MzMzNzAsIm5iZiI6MTc3NTkzMzA3MCwicGF0aCI6Ii82NjgwMDg4My81NzY5ODMyMTEtZDVkOWJhMjYtMThlMC00M2IxLTg3MWEtYzIyMjVhYzRkY2FjLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA0MTElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNDExVDE4NDQzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWI5YjNlMDViY2ZjOTYxOTE4MDA0MTU5MmEzNzhiOWI1ZTM0ZTU0NWI3NTA3OWJjNjYyZDk2NDk4YTdmN2MzZmQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9._3pvp9oTif9RwmHcvCcDDO9FHLXG7SUNZsijaYibmzQ)

This project is a professional RAG (Retrieval-Augmented Generation) assistant designed for public health professionals to navigate infectious disease surveillance manuals, CDC guidelines, and regional health memos. The project uses a Streamlit app interface and is built in a Docker container to allow for easy deployment.

## Project Organization

```
├── .github/workflows/       # Automated CI/CD pipelines
├── data/                    # Local storage for STI manuals and PDFs (Git-ignored)
├── screenshots/             # App visuals for documentation
├── src/                     # Core logic
│   ├── __init__.py
│   └── engine.py            # RAG orchestration (LlamaIndex + Groq)
├── storage/                 # Persistent vector index and embeddings (Git-ignored)
├── .env                     # Private API keys (Git-ignored)
├── .gitignore               # Prevents sensitive data from being pushed
├── query_logs.csv           # Audit trail of queries and retrieved chunks (Git-ignored)
├── app.py                   # UI with logging integration, Streamlit UI and session management
├── docker-compose.yml       # Container orchestration
├── Dockerfile               # Environment build instructions
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
```



## 🚀 Live Demo
**Hugging Face Space:** [Click here to view the app demo](https://rndayizeye-rag-surveillance-demo.hf.space)

---

## 🛠️ Technical Stack
- **LLM:** Meta Llama 3.1 (via Groq API)
- **Framework:** LlamaIndex (RAG & Data Orchestration)
- **Embeddings:** BAAI/bge-small-en-v1.5
- **UI:** Streamlit
- **Infrastructure:** Docker & Hugging Face Spaces

## 🛡️ Privacy & Security
- **Zero-Footprint:** This tool is designed with public health data sensitivity in mind. Uploaded documents are processed locally within the container and are **not** used to train global AI models.
- **Environment Management:** API keys and sensitive configurations are managed via `.env` files and are never committed to the repository.

## 📂 Features
- **Dynamic Context:** Upload specific PDFs to build a temporary knowledge base for targeted queries.
- **Verified Sources:** Every answer includes citations from your uploaded manuals to ensure accuracy.
- **Containerized:** Fully portable via Docker, allowing for deployment on internal health department servers.

## 🚦 Getting Started (Local Development)

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/your-repo.git](https://github.com/your-username/your-repo.git)
cd your-repo
2. Set Up Environment Variables
Create a .env file in the root directory:

Plaintext
GROQ_API_KEY=your_api_key_here
3. Run with Docker Compose
Bash
docker-compose up --build
Access the app at http://localhost:8501.

👨‍💻 Author
Public Health Professional | Regional Program Coordinator
Specializing in infectious disease surveillance and data analytics.
--------

