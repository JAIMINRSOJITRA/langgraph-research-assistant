"""
graph/graph.py
──────────────
Builds and compiles the LangGraph StateGraph:

START -> planner -> researcher -> analyst -> writer -> critic
                                              ^            |
                                              └── revise ──┘
critic -> (score >= threshold OR max revisions reached) -> finalize -> END
"""

from langgraph.graph import StateGraph, END

from graph.state import ResearchState
from graph.nodes import (
    planner_node,
    researcher_node,
    analyst_node,
    writer_node,
    critic_node,
    finalize_node,
    should_revise,
)


def build_graph():
    workflow = StateGraph(ResearchState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("finalize", finalize_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", "critic")

    workflow.add_conditional_edges(
        "critic",
        should_revise,
        {"revise": "writer", "end": "finalize"},
    )
    workflow.add_edge("finalize", END)

    return workflow.compile()
