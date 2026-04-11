# RAG Implementation Demo for STI Surveillance Program
This project aims to develop a demo of a RAG implementation for our STI surveillance program using a Streamlit app. It will integrate guidelines from manuals and CDC with unique instructions. Built in a Docker container, I'll document my progress on GitHub, showcasing my learning journey in programming.

# Project description
I am developing a demonstration of a RAG (Retrieval Augmented Generation) implementation tailored for our STI surveillance program. As a supervisor, I oversee a team that follows various manuals to ensure the accurate collection and entry of data. While we have established company manuals, we also adhere to CDC guidelines. However, there are often unique instructions shared through emails or presentations that haven’t yet been formally integrated into our manuals.

The goal of this project is to create a user-friendly streamlit app that effectively demonstrates the RAG implementation, allowing easy access to essential guidance and data management processes. To ensure that this demo is production-ready, I plan to build it within a Docker container, utilizing a template such as Cookiecutter, and then deploy it on Streamlit’s free server.

As I am still learning programming, I intend to approach this project step-by-step, documenting my progress and regularly publishing updates to my GitHub repository. This will not only allow me to refine my skills but also provide a valuable resource for my team and others in the field.

# Project details

# ⚖️ STI Surveillance Program Assistant (RAG)
An AI-powered Decision Support System designed to help public health professionals navigate complex STI surveillance manuals, CDC guidelines, and internal department memos.

🌟 Key Features
Privacy-First RAG: Uses local embeddings (HuggingFace BGE) to ensure sensitive document text is processed securely without being sent to third-party providers for indexing.

Hybrid Architecture: Combines local vector storage with Groq (Llama 3.1) for ultra-fast, high-quality response synthesis.

Dynamic Knowledge Base: Upload new PDFs or email memos directly through the UI and re-index the "AI brain" in seconds.

Audit-Ready: Includes a query logging system to track user needs and identification of training gaps.

Source Attribution: Every answer includes citations pointing back to the specific source document and the exact text snippet used.

🛠️ Tech Stack
Framework: LlamaIndex

Interface: Streamlit

Containerization: Docker & Docker Compose

LLM: Groq (Llama-3.1-8b-instant)

Embeddings: HuggingFace (BAAI/bge-small-en-v1.5)

Data Handling: Pandas & PyPDF

🚀 Quick Start
1. Prerequisites
Docker and Docker Compose installed.

A Groq API Key (Free at console.groq.com).

2. Configuration
Create a .env file in the root directory:

Bash
GROQ_API_KEY=your_groq_api_key_here
3. Launching the App
Run the following command in your terminal:

Bash
docker-compose up --build
The app will be available at http://localhost:8501.

📂 Project Structure
/app.py: Streamlit interface and session management.

/src/engine.py: Core RAG logic, Chat Engine configuration, and local embedding setup.

/data: Local directory for PDFs and text files (ignored by Git for privacy).

/storage: Persistent vector store (ignored by Git).

query_logs.csv: Automatic tracking of user queries (Admin only).

🛡️ Security & Privacy
This application is built with a Zero-Footprint philosophy for sensitive data:

Local Indexing: Documents are converted into mathematical vectors locally within the Docker container.

Encrypted Transit: API calls to Groq are encrypted via TLS.

Data Isolation: The /data and /storage folders are included in .gitignore to prevent accidental leakage of internal manuals to public repositories.
