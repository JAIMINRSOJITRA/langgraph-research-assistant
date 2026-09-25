"""
rag/vectorstore.py
───────────────────
ChromaDB + HuggingFace embeddings, as named in requirements.txt and README.
Provides a singleton vectorstore and the ingest_documents() entry point
used by ingest.py.
"""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from config import CHROMA_PERSIST_DIR, COLLECTION_NAME, EMBEDDING_MODEL

_embeddings = None
_vectorstore = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=CHROMA_PERSIST_DIR,
        )
    return _vectorstore


def ingest_documents(docs) -> int:
    """Add a list of langchain Document objects to the persistent vectorstore."""
    vs = get_vectorstore()
    vs.add_documents(docs)
    return len(docs)
