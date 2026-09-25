"""
graph/nodes.py
──────────────
The 5 agent functions (Planner, Researcher, Analyst, Writer, Critic) plus
the conditional edge `should_revise` that creates the Writer <-> Critic loop.

Each node takes the current ResearchState and returns a partial dict of
fields to merge back in (standard LangGraph node convention).
"""

import re

from config import get_llm, QUALITY_THRESHOLD
from rag.retriever import retrieve
from tools.web_search import web_search


def _text(response) -> str:
    """Extract plain text from a LangChain chat model response."""
    return response.content if hasattr(response, "content") else str(response)


def planner_node(state):
    llm = get_llm()
    prompt = (
        "You are a research planner. Break the following research question into "
        "3 to 5 focused, specific sub-tasks that together cover the topic thoroughly. "
        "Return ONLY a numbered list, one sub-task per line, no extra commentary.\n\n"
        f"Question: {state['query']}"
    )
    content = _text(llm.invoke(prompt))

    sub_tasks = []
    for line in content.strip().splitlines():
        line = re.sub(r"^\s*\d+[\.\)]\s*", "", line.strip())
        line = line.lstrip("-• ").strip()
        if line:
            sub_tasks.append(line)

    if not sub_tasks:
        sub_tasks = [state["query"]]

    return {"sub_tasks": sub_tasks[:5]}


def researcher_node(state):
    search_results = []
    retrieved_docs = []

    for task in state["sub_tasks"]:
        for hit in web_search(task, max_results=3):
            search_results.append({"sub_task": task, **hit})
        for doc in retrieve(task):
            retrieved_docs.append({"sub_task": task, **doc})

    return {"search_results": search_results, "retrieved_docs": retrieved_docs}


def analyst_node(state):
    llm = get_llm()

    web_summary = "\n".join(
        f"- [{r.get('sub_task', '')}] {r.get('title', '')}: {r.get('snippet', '')}"
        for r in state["search_results"][:15]
    ) or "No web results."

    doc_summary = "\n".join(
        f"- [{d.get('sub_task', '')}] {d.get('content', '')[:300]}"
        for d in state["retrieved_docs"][:15]
    ) or "No local knowledge-base results."

    prompt = (
        "You are a research analyst. Synthesize the raw findings below into a clear, "
        "structured analysis (short headed sections) that will be used to write a "
        f"report answering: {state['query']}\n\n"
        f"WEB RESULTS:\n{web_summary}\n\n"
        f"KNOWLEDGE BASE RESULTS:\n{doc_summary}\n"
    )
    return {"analysis": _text(llm.invoke(prompt))}


def writer_node(state):
    llm = get_llm()

    if state.get("critique"):
        prompt = (
            "Revise the following research report based on this critique.\n\n"
            f"ORIGINAL QUERY: {state['query']}\n\n"
            f"ANALYSIS:\n{state['analysis']}\n\n"
            f"PREVIOUS DRAFT:\n{state.get('draft_report', '')}\n\n"
            f"CRITIQUE TO ADDRESS:\n{state['critique']}\n\n"
            "Write an improved, complete report in Markdown."
        )
    else:
        prompt = (
            "Write a thorough, well-structured research report in Markdown "
            f"answering: {state['query']}\n\n"
            f"Base it on this analysis:\n{state['analysis']}"
        )

    draft_report = _text(llm.invoke(prompt))
    return {
        "draft_report": draft_report,
        "revision_count": state.get("revision_count", 0) + 1,
    }


def critic_node(state):
    llm = get_llm()
    prompt = (
        "You are a strict quality critic. Review the report below and respond with "
        "exactly this format:\n"
        "SCORE: <integer 1-10>\n"
        "CRITIQUE: <one short paragraph of specific, actionable feedback>\n\n"
        f"QUERY: {state['query']}\n\n"
        f"REPORT:\n{state['draft_report']}"
    )
    content = _text(llm.invoke(prompt))

    score_match = re.search(r"SCORE:\s*(\d+)", content, re.IGNORECASE)
    quality_score = max(1, min(10, int(score_match.group(1)))) if score_match else 5

    critique_match = re.search(r"CRITIQUE:\s*(.+)", content, re.IGNORECASE | re.DOTALL)
    critique = critique_match.group(1).strip() if critique_match else content.strip()

    return {"quality_score": quality_score, "critique": critique}


def finalize_node(state):
    """Copy the accepted (or capped) draft into final_report."""
    return {"final_report": state["draft_report"]}


def should_revise(state) -> str:
    """Conditional edge after the Critic: loop back to Writer, or finish."""
    if state["quality_score"] >= QUALITY_THRESHOLD or state["revision_count"] >= state["max_revisions"]:
        return "end"
    return "revise"
