"""
rag/retriever.py
─────────────────
Thin wrapper around the vectorstore's similarity search, used by the
Researcher agent to pull local knowledge-base context for each sub-task.
"""

from config import TOP_K
from rag.vectorstore import get_vectorstore


def retrieve(query: str, k: int = None):
    """Return top-k similar chunks as [{content, metadata}, ...].

    Fails soft (returns []) if the collection is empty or unreachable,
    so a fresh clone that hasn't run ingest.py yet doesn't crash the graph.
    """
    k = k or TOP_K
    try:
        results = get_vectorstore().similarity_search(query, k=k)
    except Exception:
        return []
    return [{"content": doc.page_content, "metadata": doc.metadata} for doc in results]
