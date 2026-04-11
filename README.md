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

# STI Surveillance (RAG)

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

## App screenshot 

![App Screenshot](https://private-user-images.githubusercontent.com/66800883/576983211-d5d9ba26-18e0-43b1-871a-c2225ac4dcac.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzU5MzMzNzAsIm5iZiI6MTc3NTkzMzA3MCwicGF0aCI6Ii82NjgwMDg4My81NzY5ODMyMTEtZDVkOWJhMjYtMThlMC00M2IxLTg3MWEtYzIyMjVhYzRkY2FjLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA0MTElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNDExVDE4NDQzMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWI5YjNlMDViY2ZjOTYxOTE4MDA0MTU5MmEzNzhiOWI1ZTM0ZTU0NWI3NTA3OWJjNjYyZDk2NDk4YTdmN2MzZmQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9._3pvp9oTif9RwmHcvCcDDO9FHLXG7SUNZsijaYibmzQ)

This project is a professional RAG (Retrieval-Augmented Generation) assistant designed for public health professionals to navigate infectious disease surveillance manuals, CDC guidelines, and regional health memos. The project uses a Streamlit app interface and is built in a Docker container to allow for easy deployment.

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         sti_surveillance_rag and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── sti_surveillance_rag   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes sti_surveillance_rag a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
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

