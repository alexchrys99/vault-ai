# 🔒 Vault AI: Enterprise Multi-Tenant RAG SaaS

Vault AI is a fully local, containerized Retrieval-Augmented Generation (RAG) application designed for corporate environments. It allows multiple authenticated users to securely upload, encrypt, and chat with their confidential documents without data ever leaving the local network.

## 🌟 Key Features
* **Multi-Tenant Row-Level Security:** Documents are mathematically embedded and tagged with user IDs. Users can only query documents they explicitly uploaded.
* **Conversational Memory:** The AI maintains session history, allowing for natural, contextual follow-up questions.
* **100% Local Processing:** Powered by Meta's Llama 3.2 via Ollama, ensuring zero data leakage to external APIs (OpenAI, Anthropic, etc.).
* **Microservice Architecture:** Fully Dockerized with a shared-base image to bypass Linux filesystem constraints, separating the REST API backend from the stateful frontend.

## 🛠️ Tech Stack
* **AI & Embeddings:** Llama 3.2, Nomic-Embed-Text, Ollama
* **Orchestration:** LangChain, ChromaDB (Vector Store)
* **Backend:** FastAPI, Python, SQLite, Bcrypt (Authentication)
* **Frontend:** Streamlit
* **DevOps:** Docker, Docker Compose

## 🚀 Quick Start
To run this application locally, ensure you have Docker and Docker Compose installed, as well as an active instance of Ollama.

1. Clone the repository:
   git clone [https://github.com/YOUR_USERNAME/vault-ai.git](https://github.com/YOUR_USERNAME/vault-ai.git)
   cd vault-ai

2. Build and launch the microservices:
   docker compose up --build

3. Access the Secure Vault UI at http://localhost:8501.

## 🔐 Security Note
This repository does not include the users.db or chroma_db directories. Upon first launch, the SQLite and Vector databases will be automatically generated locally to ensure maximum data privacy.
