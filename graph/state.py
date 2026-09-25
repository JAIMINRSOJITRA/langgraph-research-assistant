"""
graph/state.py
──────────────
Shared state schema passed between every node in the LangGraph pipeline.
Field names match exactly what app.py and main.py already build as
`initial_state`, so no other file needs to change.
"""

from typing import TypedDict, List, Dict, Any


class ResearchState(TypedDict):
    messages: List[Any]
    query: str
    sub_tasks: List[str]
    search_results: List[Dict[str, Any]]
    retrieved_docs: List[Dict[str, Any]]
    analysis: str
    draft_report: str
    critique: str
    quality_score: int
    revision_count: int
    max_revisions: int
    final_report: str
