"""
main.py
───────
Entry point for the Multi-Agent AI Research Assistant.

Modes:
  python main.py                   → interactive REPL
  python main.py --demo            → run a demo query automatically
  python main.py "your question"   → single query from CLI args

The script:
  1. Compiles the LangGraph pipeline
  2. Accepts a research query
  3. Invokes the graph (Planner → Researcher → Analyst → Writer ⇄ Critic)
  4. Prints the final accepted report with quality metadata

Setup required (one-time):
  pip install -r requirements.txt
  cp .env.example .env       # add your GROQ_API_KEY
  python ingest.py           # populate local knowledge base
"""

import sys
from graph.graph import build_graph
from config import MAX_REVISIONS, QUALITY_THRESHOLD

# Sample queries for --demo mode
DEMO_QUERIES = [
    "What are the latest breakthroughs in large language models and how are they changing AI?",
    "How does quantum computing work and what industries will it disrupt first?",
    "What are the most effective current solutions to climate change?",
]

BANNER = """
╔══════════════════════════════════════════════════════════╗
║      🔬  Multi-Agent AI Research Assistant               ║
║      Powered by LangGraph + Groq/Ollama                  ║
║                                                          ║
║  Agents: Planner → Researcher → Analyst → Writer ⇄ Critic║
╚══════════════════════════════════════════════════════════╝
"""


def run_research(graph, query: str) -> str:
    """
    Execute the full research pipeline for a given query.

    Args:
        graph: compiled LangGraph StateGraph
        query: research question string

    Returns:
        The final report string
    """
    sep = "═" * 60
    print(f"\n{sep}")
    print(f"🔬  Research Query: {query}")
    print(sep)

    # Initial state — all fields must be provided (TypedDict is strict)
    initial_state = {
        "messages":       [],
        "query":          query,
        "sub_tasks":      [],
        "search_results": [],
        "retrieved_docs": [],
        "analysis":       "",
        "draft_report":   "",
        "critique":       "",
        "quality_score":  0,
        "revision_count": 0,
        "max_revisions":  MAX_REVISIONS,
        "final_report":   "",
    }

    result = graph.invoke(initial_state)

    # final_report is set if score >= threshold; fallback to draft if capped
    report = result.get("final_report") or result.get("draft_report", "No report generated.")

    # ── Print output ──────────────────────────────────────────────────────────
    print(f"\n{sep}")
    print("📄  FINAL REPORT")
    print(sep)
    print(report)
    print(f"\n{'─' * 60}")
    print(f"⭐  Final Score  : {result.get('quality_score', 'N/A')}/10")
    print(f"📝  Revisions    : {result.get('revision_count', 0)}")
    print(f"🎯  Threshold    : {QUALITY_THRESHOLD}/10")
    print(f"🔁  Max Revisions: {MAX_REVISIONS}")
    print(f"{'─' * 60}\n")

    return report


def main():
    print(BANNER)

    # ── Build the graph ───────────────────────────────────────────────────────
    print("🔧  Compiling LangGraph pipeline...")
    graph = build_graph()
    print("✅  Graph compiled successfully!\n")

    # ── Parse CLI args ────────────────────────────────────────────────────────
    args = sys.argv[1:]

    if args and args[0] == "--demo":
        # Single demo run then exit
        run_research(graph, DEMO_QUERIES[0])
        return

    if args:
        # Query passed directly as CLI arg
        run_research(graph, " ".join(args))
        return

    # ── Interactive REPL ──────────────────────────────────────────────────────
    print("💡  Commands:")
    print("    'demo'    → run a sample research query")
    print("    'exit'    → quit")
    print("    anything  → your research question\n")

    while True:
        try:
            query = input("Research ❯ ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋  Goodbye!")
            break

        if not query:
            continue

        if query.lower() in ("exit", "quit", "q"):
            print("👋  Goodbye!")
            break

        if query.lower() == "demo":
            run_research(graph, DEMO_QUERIES[0])
            continue

        if query.lower() == "demo2":
            run_research(graph, DEMO_QUERIES[1])
            continue

        try:
            run_research(graph, query)
        except KeyboardInterrupt:
            print("\n⚠️  Research interrupted. Enter a new query or 'exit'.")
        except Exception as e:
            print(f"\n❌  Error: {e}")
            print("    Check your .env file and try again.\n")


if __name__ == "__main__":
    main()
