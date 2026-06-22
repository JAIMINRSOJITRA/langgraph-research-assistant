# 🔬 Multi-Agent AI Research Assistant

> A production-quality LangGraph project featuring 5 specialized AI agents, a self-critique feedback loop, RAG (Retrieval-Augmented Generation), and live web search.

---

## 🏗️ Architecture

```
START
  ↓
[Planner]       → breaks query into 3–5 focused sub-tasks
  ↓
[Researcher]    → fetches data (DuckDuckGo web + ChromaDB RAG)
  ↓
[Analyst]       → synthesizes findings into structured analysis
  ↓
[Writer]   ←────────────────────────────────┐
  ↓                                          │ revise loop
[Critic]   → score < 7/10? → send back ────┘
  ↓
 END         (score ≥ 7/10 OR max revisions reached)
```

---

## ⚡ Quick Start

```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# → Add your GROQ_API_KEY (free at console.groq.com)

# 3. Populate knowledge base
python ingest.py

# 4. Run!
python main.py                         # interactive mode
python main.py --demo                  # demo query
python main.py "How does RAG work?"   # single query
```

---

## 📁 File Structure

```
langgraph_research_assistant/
├── config.py              # env config + LLM factory
├── ingest.py              # one-time KB population script
├── main.py                # entry point / REPL
├── requirements.txt
├── .env.example
│
├── graph/
│   ├── state.py           # ResearchState TypedDict
│   ├── nodes.py           # 5 agent functions + conditional edge
│   └── graph.py           # StateGraph builder
│
├── rag/
│   ├── vectorstore.py     # ChromaDB + HuggingFace embeddings
│   └── retriever.py       # similarity search wrapper
│
└── tools/
    └── web_search.py      # DuckDuckGo wrapper
```

---

## 🤖 The 5 Agents

| Agent | Role | Input → Output |
|-------|------|----------------|
| **Planner** | Query decomposer | query → sub_tasks |
| **Researcher** | Data gatherer | sub_tasks → search_results + retrieved_docs |
| **Analyst** | Synthesizer | raw data → structured analysis |
| **Writer** | Report author | analysis + critique → draft_report |
| **Critic** | Quality gatekeeper | draft_report → score + critique |

---

## 🔑 What Makes This a Strong LangGraph Portfolio Project

1. **Cyclic graph** — The Writer↔Critic loop is impossible in simple chains
2. **Conditional edges** — `should_revise()` dynamically routes the graph
3. **Dual data sources** — Web search + RAG working together
4. **Structured state** — TypedDict ensures type safety across all agents
5. **Configurable quality threshold** — Tune via QUALITY_THRESHOLD env var

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `groq` | `groq` or `ollama` |
| `GROQ_API_KEY` | — | Get free at console.groq.com |
| `GROQ_MODEL` | `llama-3.1-70b-versatile` | Any Groq model |
| `MAX_REVISIONS` | `3` | Max Writer↔Critic loops |
| `QUALITY_THRESHOLD` | `7` | Min score (1–10) to accept report |
| `TOP_K` | `3` | RAG chunks retrieved per sub-task |
