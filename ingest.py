"""
ingest.py
─────────
ONE-TIME SETUP SCRIPT — run this before main.py to populate the ChromaDB
knowledge base with seed documents.

The Researcher agent will use these docs via RAG (semantic similarity search)
to supplement live web search results.

Add your own documents to the DOCS list below, then re-run this script.
Supported: plain text content, any topic.

Usage:
    python ingest.py
"""

from langchain_core.documents import Document
from rag.vectorstore import ingest_documents

# ── Seed Knowledge Base ───────────────────────────────────────────────────────
# Add or extend these documents to customize the assistant's local knowledge.
DOCS = [
    Document(
        page_content=(
            "Artificial intelligence (AI) refers to the simulation of human intelligence "
            "in machines. Modern AI includes machine learning, deep learning, natural language "
            "processing, and computer vision. AI systems learn from data, improve with experience, "
            "and can perform tasks that typically require human intelligence."
        ),
        metadata={"topic": "AI", "source": "seed"},
    ),
    Document(
        page_content=(
            "Large Language Models (LLMs) are deep learning models trained on massive text datasets. "
            "They can generate text, answer questions, summarize documents, translate languages, "
            "and write code. Examples include GPT-4, Claude, Llama, and Gemini. LLMs use transformer "
            "architecture with attention mechanisms to understand context."
        ),
        metadata={"topic": "LLMs", "source": "seed"},
    ),
    Document(
        page_content=(
            "LangGraph is a library for building stateful, multi-agent LLM applications. "
            "It uses a graph model where nodes are agents or tools and edges define execution flow. "
            "Unlike simple chains, LangGraph supports CYCLES — allowing agents to loop, self-critique, "
            "and retry until a quality threshold is met. This makes it ideal for autonomous agents."
        ),
        metadata={"topic": "LangGraph", "source": "seed"},
    ),
    Document(
        page_content=(
            "RAG (Retrieval-Augmented Generation) combines vector search with LLM generation. "
            "It fetches relevant document chunks from a knowledge base BEFORE the LLM generates "
            "a response. This grounds the output in factual data, reduces hallucinations, and allows "
            "the model to answer questions about custom or recent content not in its training data."
        ),
        metadata={"topic": "RAG", "source": "seed"},
    ),
    Document(
        page_content=(
            "Quantum computing uses quantum bits (qubits) that can exist in superposition — "
            "simultaneously 0 and 1. Entanglement links qubits so measuring one instantly affects "
            "others. This enables quantum parallelism, promising exponential speedups for optimization, "
            "cryptography breaking, molecular simulation, and problems intractable for classical computers."
        ),
        metadata={"topic": "Quantum Computing", "source": "seed"},
    ),
    Document(
        page_content=(
            "Climate change refers to long-term shifts in global temperatures and weather patterns. "
            "Since the 1800s, human activities — especially burning fossil fuels — have driven a "
            "1.1°C rise in global average temperatures. Consequences include rising sea levels, "
            "more frequent extreme weather events, ecosystem disruption, and threats to food security."
        ),
        metadata={"topic": "Climate Change", "source": "seed"},
    ),
    Document(
        page_content=(
            "Vector embeddings are numerical representations of text in high-dimensional space. "
            "Semantically similar texts cluster close together in this space. "
            "Embeddings power semantic search (find meaning, not just keywords), RAG pipelines, "
            "recommendation systems, and clustering. Popular models: all-MiniLM-L6-v2, text-embedding-3."
        ),
        metadata={"topic": "Embeddings", "source": "seed"},
    ),
    Document(
        page_content=(
            "Reinforcement Learning from Human Feedback (RLHF) trains AI models using human preferences. "
            "A reward model is trained on human rankings of model outputs. The LLM is then fine-tuned "
            "via PPO to maximize predicted human preference scores. RLHF is how ChatGPT and Claude were "
            "aligned to be helpful, harmless, and honest."
        ),
        metadata={"topic": "RLHF", "source": "seed"},
    ),
    Document(
        page_content=(
            "Multi-agent AI systems use multiple specialized LLM agents that collaborate to solve "
            "complex tasks. Each agent has a specific role (planner, researcher, writer, critic). "
            "Coordination frameworks like LangGraph, AutoGen, and CrewAI manage agent communication, "
            "state sharing, and execution order. Multi-agent systems outperform single agents on "
            "complex, multi-step tasks."
        ),
        metadata={"topic": "Multi-Agent AI", "source": "seed"},
    ),
    Document(
        page_content=(
            "ChromaDB is an open-source AI-native vector database. It stores embeddings persistently "
            "on disk and supports fast similarity search (ANN). It integrates directly with LangChain "
            "and LlamaIndex. ChromaDB is ideal for RAG pipelines, semantic search, and building "
            "personal knowledge bases without needing a cloud vector DB."
        ),
        metadata={"topic": "ChromaDB", "source": "seed"},
    ),
]


if __name__ == "__main__":
    print("📥  Ingesting knowledge base documents into ChromaDB...")
    print(f"    Documents to ingest: {len(DOCS)}")
    print()

    ingest_documents(DOCS)

    print()
    print(f"✅  Successfully ingested {len(DOCS)} documents!")
    print("    Vector store saved to: ./chroma_db")
    print()
    print("👉  Next step: python main.py")
