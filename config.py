"""
config.py
─────────
Central configuration. Reads from .env via python-dotenv.
Also provides get_llm() factory so all agents share the same LLM instance.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Provider ──────────────────────────────────────────────────────────────
LLM_PROVIDER    = os.getenv("LLM_PROVIDER", "groq")

# ── Groq ──────────────────────────────────────────────────────────────────────
GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL      = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

# ── Ollama ────────────────────────────────────────────────────────────────────
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ── RAG / ChromaDB ────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME    = os.getenv("COLLECTION_NAME", "research_docs")
EMBEDDING_MODEL    = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K              = int(os.getenv("TOP_K", "3"))

# ── Quality Control ───────────────────────────────────────────────────────────
MAX_REVISIONS      = int(os.getenv("MAX_REVISIONS", "3"))
QUALITY_THRESHOLD  = int(os.getenv("QUALITY_THRESHOLD", "7"))


def get_llm():
    """
    Factory: returns the configured ChatModel instance.
    Switch between Groq (cloud) and Ollama (local) via LLM_PROVIDER env var.
    """
    if LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

    from langchain_groq import ChatGroq
    if not GROQ_API_KEY:
        raise EnvironmentError(
            "GROQ_API_KEY is not set.\n"
            "→ Copy .env.example to .env and add your key from console.groq.com"
        )
    return ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL)
