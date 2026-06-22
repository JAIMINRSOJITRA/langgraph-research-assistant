"""
app.py
──────
Streamlit UI for the Multi-Agent AI Research Assistant.

Run with:
    streamlit run app.py
"""

import os
import sys
import time
import threading
import queue
from datetime import datetime
from pathlib import Path

import streamlit as st

# ── Page Config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Import Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Dark Background ── */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 50%, #0a0e1a 100%);
    color: #e2e8f0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1629 0%, #0a0e1a 100%);
    border-right: 1px solid rgba(139, 92, 246, 0.2);
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* ── Main Header ── */
.main-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
    background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(6,182,212,0.1));
    border-radius: 20px;
    border: 1px solid rgba(139, 92, 246, 0.2);
    margin-bottom: 2rem;
}
.main-header h1 {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}
.main-header p {
    color: #94a3b8;
    font-size: 1rem;
    margin: 0;
}

/* ── Agent Status Cards ── */
.agent-grid {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin: 1.5rem 0;
}
.agent-card {
    flex: 1;
    min-width: 130px;
    padding: 1rem 0.75rem;
    border-radius: 12px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(15,22,41,0.8);
    transition: all 0.3s ease;
    font-size: 0.8rem;
}
.agent-card.idle {
    opacity: 0.5;
    border-color: rgba(148,163,184,0.2);
}
.agent-card.active {
    border-color: #a78bfa;
    background: rgba(139,92,246,0.15);
    box-shadow: 0 0 20px rgba(139,92,246,0.3);
    animation: pulse-glow 1.5s infinite;
}
.agent-card.done {
    border-color: #34d399;
    background: rgba(52,211,153,0.1);
}
.agent-card.error {
    border-color: #f87171;
    background: rgba(248,113,113,0.1);
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 15px rgba(139,92,246,0.3); }
    50%       { box-shadow: 0 0 30px rgba(139,92,246,0.6); }
}
.agent-icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
.agent-name { font-weight: 600; color: #e2e8f0; margin-bottom: 0.2rem; }
.agent-status-text { color: #94a3b8; font-size: 0.72rem; }

/* ── Search Box ── */
.stTextArea textarea {
    background: rgba(15,22,41,0.9) !important;
    border: 2px solid rgba(139,92,246,0.4) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    transition: border-color 0.3s ease !important;
}
.stTextArea textarea:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.2) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #06b6d4) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.5) !important;
}

/* ── Log Box ── */
.log-box {
    background: rgba(10,14,26,0.9);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    color: #a0aec0;
    max-height: 280px;
    overflow-y: auto;
    margin: 1rem 0;
    line-height: 1.7;
}
.log-box .log-planner   { color: #c084fc; }
.log-box .log-researcher { color: #67e8f9; }
.log-box .log-analyst   { color: #fbbf24; }
.log-box .log-writer    { color: #86efac; }
.log-box .log-critic    { color: #f87171; }
.log-box .log-system    { color: #94a3b8; }

/* ── Report Card ── */
.report-card {
    background: rgba(15,22,41,0.9);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
    line-height: 1.8;
    color: #e2e8f0;
}
.score-badge {
    display: inline-block;
    padding: 0.4rem 1.2rem;
    border-radius: 50px;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 1rem;
}
.score-high { background: rgba(52,211,153,0.2); color: #34d399; border: 1px solid #34d399; }
.score-mid  { background: rgba(251,191,36,0.2);  color: #fbbf24; border: 1px solid #fbbf24; }
.score-low  { background: rgba(248,113,113,0.2); color: #f87171; border: 1px solid #f87171; }

/* ── History Items ── */
.history-item {
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.2);
    margin-bottom: 0.5rem;
    cursor: pointer;
    font-size: 0.82rem;
    color: #c4b5fd;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: all 0.2s ease;
}
.history-item:hover {
    background: rgba(139,92,246,0.2);
    border-color: rgba(139,92,246,0.5);
}

/* ── Divider ── */
.custom-divider {
    border: none;
    border-top: 1px solid rgba(139,92,246,0.2);
    margin: 1.5rem 0;
}

/* ── Slider & Select ── */
.stSlider > div > div > div {
    background: linear-gradient(135deg, #7c3aed, #06b6d4) !important;
}
.stSelectbox select {
    background: rgba(15,22,41,0.9) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(139,92,246,0.3) !important;
    border-radius: 8px !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: rgba(15,22,41,0.8);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 12px;
    padding: 1rem !important;
}
[data-testid="metric-container"] label { color: #94a3b8 !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #a78bfa !important; font-size: 1.6rem !important; }

/* ── Info / Warning boxes ── */
.stAlert {
    border-radius: 10px !important;
    border: none !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #a78bfa !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(10,14,26,0.5); }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.5); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(139,92,246,0.8); }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Session State Init ─────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "history":        [],
        "current_report": None,
        "current_score":  None,
        "current_revs":   None,
        "agent_states":   {n: "idle" for n in ["planner","researcher","analyst","writer","critic"]},
        "logs":           [],
        "is_running":     False,
        "error":          None,
        "prefill_query":  "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()


# ── Agent Metadata ─────────────────────────────────────────────────────────────
AGENTS = [
    {"key": "planner",    "icon": "🧠", "name": "Planner",    "desc": "Breaks query into sub-tasks"},
    {"key": "researcher", "icon": "🔍", "name": "Researcher", "desc": "Searches web + local docs"},
    {"key": "analyst",    "icon": "📊", "name": "Analyst",    "desc": "Synthesizes findings"},
    {"key": "writer",     "icon": "✍️",  "name": "Writer",     "desc": "Writes the report"},
    {"key": "critic",     "icon": "⭐", "name": "Critic",     "desc": "Scores & reviews"},
]

STATUS_LABELS = {
    "idle":   "Waiting...",
    "active": "Working...",
    "done":   "Done ✓",
    "error":  "Error ✗",
}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem 0;">
        <div style="font-size:2.5rem">🔬</div>
        <div style="font-weight:700; font-size:1.1rem; color:#a78bfa;">Research Assistant</div>
        <div style="font-size:0.75rem; color:#64748b;">Powered by LangGraph + Groq</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(139,92,246,0.2);margin:0.5rem 0 1rem 0;'>", unsafe_allow_html=True)

    st.markdown("**⚙️ Settings**")

    llm_provider = st.selectbox(
        "LLM Provider",
        options=["groq", "ollama"],
        index=0,
        help="Groq = fast cloud API. Ollama = local model (must be installed)."
    )

    # ── Groq model selector ──
    if llm_provider == "groq":
        import urllib.request as _ureq, json as _json2
        from dotenv import dotenv_values

        # Load API key from .env
        _env        = dotenv_values(".env")
        _groq_key   = _env.get("GROQ_API_KEY", "")

        groq_available   = False
        groq_model_list  = []

        # Preferred chat models (LLM-only, no whisper/tts)
        PREFERRED_GROQ_MODELS = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
            "llama3-groq-70b-8192-tool-use-preview",
            "llama3-groq-8b-8192-tool-use-preview",
        ]

        if _groq_key:
            try:
                _req = _ureq.Request(
                    "https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {_groq_key}"}
                )
                _resp = _ureq.urlopen(_req, timeout=3)
                _data = _json2.loads(_resp.read().decode())
                # Filter to only chat/text models (exclude whisper, tts, vision-only)
                _all  = [m["id"] for m in _data.get("data", [])]
                # Keep only models in our preferred list that are actually available
                groq_model_list = [m for m in PREFERRED_GROQ_MODELS if m in _all]
                # If none matched preferred, show all text-like models
                if not groq_model_list:
                    groq_model_list = [m for m in _all if "whisper" not in m and "tts" not in m]
                groq_available = True
            except Exception:
                groq_available = False

        if groq_available and groq_model_list:
            st.markdown(
                f"<div style='color:#67e8f9;font-size:0.78rem;margin-bottom:0.4rem;'>"
                f"✅ Groq connected — <b>{len(groq_model_list)}</b> model(s) available</div>",
                unsafe_allow_html=True
            )
            groq_model = st.selectbox(
                "Groq Model",
                options=groq_model_list,
                index=0,
                help="Live list of available Groq models from your account"
            )
        else:
            # Fallback to static list if API unreachable
            groq_model = st.selectbox(
                "Groq Model",
                options=[
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant",
                    "llama3-70b-8192",
                    "llama3-8b-8192",
                    "mixtral-8x7b-32768",
                    "gemma2-9b-it",
                ],
                index=0,
                help="Select the Groq-hosted model to use"
            )

        ollama_model = "llama3"  # default, unused
        st.markdown(f"""
        <div style='background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.3);
        border-radius:8px;padding:0.6rem 0.8rem;font-size:0.75rem;color:#67e8f9;margin-top:0.3rem;'>
        ☁️ <b>Cloud API</b> — Fast, free tier available<br>
        <span style='color:#64748b;'>Active: <code style='color:#67e8f9'>{groq_model}</code></span>
        </div>
        """, unsafe_allow_html=True)

    # ── Ollama model selector ──
    else:
        groq_model = "llama-3.1-70b-versatile"  # default, unused

        # ── Dynamically fetch installed models from Ollama API ──
        import urllib.request, json as _json

        ollama_running   = False
        installed_models = []

        try:
            req  = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
            data = _json.loads(req.read().decode())
            installed_models = [m["name"] for m in data.get("models", [])]
            ollama_running = True
        except Exception:
            ollama_running = False

        if ollama_running and installed_models:
            # Green status
            st.markdown(
                "<div style='color:#34d399;font-size:0.78rem;margin-bottom:0.4rem;'>"
                "✅ Ollama running — "
                f"<b>{len(installed_models)}</b> model(s) installed</div>",
                unsafe_allow_html=True
            )
            ollama_model = st.selectbox(
                "Ollama Model",
                options=installed_models,
                index=0,
                help="These are the models already pulled on your machine."
            )
            st.markdown(f"""
            <div style='background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.3);
            border-radius:8px;padding:0.6rem 0.8rem;font-size:0.75rem;color:#34d399;margin-top:0.3rem;'>
            💻 <b>Local Model</b> — Private &amp; offline<br>
            <span style='color:#94a3b8;'>Active: <code style='color:#34d399'>{ollama_model}</code></span>
            </div>
            """, unsafe_allow_html=True)

        elif ollama_running and not installed_models:
            # Ollama running but no models pulled
            ollama_model = "llama3"   # fallback placeholder
            st.markdown("""
            <div style='background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.3);
            border-radius:8px;padding:0.8rem;font-size:0.78rem;color:#fbbf24;'>
            ⚠️ <b>Ollama is running but no models are installed!</b><br><br>
            Open a terminal and run one of these:<br>
            <code style='color:#fbbf24;display:block;margin-top:0.4rem;'>ollama pull llama3</code>
            <code style='color:#fbbf24;display:block;'>ollama pull mistral</code>
            <code style='color:#fbbf24;display:block;'>ollama pull phi3</code>
            <br><span style='color:#94a3b8;'>Then refresh this page.</span>
            </div>
            """, unsafe_allow_html=True)

        else:
            # Ollama not running at all
            ollama_model = "llama3"   # fallback placeholder
            st.markdown("""
            <div style='background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.3);
            border-radius:8px;padding:0.8rem;font-size:0.78rem;color:#f87171;'>
            ❌ <b>Ollama is not running!</b><br><br>
            <b>Step 1:</b> Download from <a href='https://ollama.com' style='color:#f87171;'>ollama.com</a><br>
            <b>Step 2:</b> Install &amp; start Ollama<br>
            <b>Step 3:</b> Run: <code style='color:#f87171;'>ollama pull llama3</code><br>
            <b>Step 4:</b> Refresh this page<br><br>
            <span style='color:#94a3b8;'>Or switch provider to <b>Groq</b> (cloud, works now!)</span>
            </div>
            """, unsafe_allow_html=True)

    max_revisions = st.slider(
        "Max Revisions",
        min_value=1, max_value=5, value=3,
        help="How many times the Writer can be asked to improve the report"
    )

    quality_threshold = st.slider(
        "Quality Threshold",
        min_value=5, max_value=10, value=7,
        help="Minimum Critic score (1–10) needed to accept the report"
    )

    st.markdown("<hr style='border-color:rgba(139,92,246,0.2);margin:1rem 0;'>", unsafe_allow_html=True)

    if st.button("🆕  New Research"):
        st.session_state.current_report = None
        st.session_state.current_score  = None
        st.session_state.current_revs   = None
        st.session_state.agent_states   = {n: "idle" for n in ["planner","researcher","analyst","writer","critic"]}
        st.session_state.logs           = []
        st.session_state.is_running     = False
        st.session_state.error          = None
        st.rerun()

    # ── History ──
    if st.session_state.history:
        st.markdown("<hr style='border-color:rgba(139,92,246,0.2);margin:1rem 0;'>", unsafe_allow_html=True)
        st.markdown("**🕒 Research History**")
        for i, item in enumerate(reversed(st.session_state.history[-8:])):
            short_q = item["query"][:45] + "..." if len(item["query"]) > 45 else item["query"]
            st.markdown(f"""<div class="history-item" title="{item['query']}">📄 {short_q}</div>""",
                        unsafe_allow_html=True)


# ── Main Panel ─────────────────────────────────────────────────────────────────
# Header
st.markdown("""
<div class="main-header">
    <h1>🔬 Multi-Agent AI Research Assistant</h1>
    <p>Planner &nbsp;→&nbsp; Researcher &nbsp;→&nbsp; Analyst &nbsp;→&nbsp; Writer &nbsp;⇄&nbsp; Critic</p>
</div>
""", unsafe_allow_html=True)


# ── Input Section ─────────────────────────────────────────────────────────────
# Callback to safely set text area content
def set_demo_query(q):
    st.session_state.query_input = q

query = st.text_area(
    "🔎 Enter your research question",
    placeholder="e.g. What are the latest breakthroughs in large language models?",
    height=100,
    key="query_input",
    label_visibility="visible",
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_btn = st.button("🚀  Start Research", disabled=st.session_state.is_running)

# ── Demo Buttons ──────────────────────────────────────────────────────────────
st.markdown("<div style='text-align:center; margin:-0.5rem 0 1rem 0; color:#64748b; font-size:0.8rem;'>or try a demo question</div>", unsafe_allow_html=True)
dc1, dc2, dc3 = st.columns(3)

with dc1:
    st.button("💡 Large Language Models", use_container_width=True, on_click=set_demo_query, args=("What are the latest breakthroughs in large language models and how are they changing AI?",))
with dc2:
    st.button("⚛️ Quantum Computing", use_container_width=True, on_click=set_demo_query, args=("How does quantum computing work and what industries will it disrupt first?",))
with dc3:
    st.button("🌍 Climate Change", use_container_width=True, on_click=set_demo_query, args=("What are the most effective current solutions to climate change?",))


# ── Agent Status Grid ─────────────────────────────────────────────────────────
st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
st.markdown("**🤖 Agent Pipeline**")

agent_cols = st.columns(5)
agent_placeholders = {}
for i, agent in enumerate(AGENTS):
    with agent_cols[i]:
        agent_placeholders[agent["key"]] = st.empty()


def render_agent_card(placeholder, agent, state):
    status_class = state
    status_text  = STATUS_LABELS.get(state, "Waiting...")
    placeholder.markdown(f"""
    <div class="agent-card {status_class}">
        <div class="agent-icon">{agent['icon']}</div>
        <div class="agent-name">{agent['name']}</div>
        <div class="agent-status-text">{status_text}</div>
    </div>
    """, unsafe_allow_html=True)


# Render initial states
for agent in AGENTS:
    render_agent_card(agent_placeholders[agent["key"]], agent, st.session_state.agent_states[agent["key"]])


# ── Live Logs ─────────────────────────────────────────────────────────────────
st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
log_header_col, _ = st.columns([3,1])
with log_header_col:
    st.markdown("**📡 Live Agent Logs**")

log_placeholder = st.empty()

def render_logs():
    if not st.session_state.logs:
        log_placeholder.markdown("""
        <div class="log-box" style="color:#4a5568; font-style:italic;">
            Logs will appear here when research starts...
        </div>""", unsafe_allow_html=True)
        return

    lines_html = ""
    for log in st.session_state.logs[-60:]:
        agent_cls  = log.get("agent", "system")
        msg        = log.get("msg", "")
        ts         = log.get("ts", "")
        lines_html += f'<div class="log-{agent_cls}">[{ts}] {msg}</div>'

    log_placeholder.markdown(f'<div class="log-box">{lines_html}</div>', unsafe_allow_html=True)

render_logs()


# ── Research Results ──────────────────────────────────────────────────────────
result_placeholder = st.empty()

def render_results():
    if st.session_state.current_report:
        score = st.session_state.current_score or 0
        revs  = st.session_state.current_revs or 0

        if score >= 8:
            badge_cls = "score-high"
            badge_emoji = "🌟"
        elif score >= 6:
            badge_cls = "score-mid"
            badge_emoji = "⭐"
        else:
            badge_cls = "score-low"
            badge_emoji = "📝"

        # Metrics row
        m1, m2, m3, m4 = result_placeholder.columns(4)
        m1.metric("Quality Score", f"{score}/10")
        m2.metric("Revisions Made", revs)
        m3.metric("Threshold", f"{quality_threshold}/10")
        m4.metric("Status", "✅ Accepted" if score >= quality_threshold else "📝 Capped")

render_results()

report_placeholder = st.empty()

def render_report():
    if st.session_state.current_report:
        score = st.session_state.current_score or 0
        if score >= 8:
            badge_cls, badge_label = "score-high", f"🌟 Score: {score}/10 — Excellent!"
        elif score >= 6:
            badge_cls, badge_label = "score-mid",  f"⭐ Score: {score}/10 — Good"
        else:
            badge_cls, badge_label = "score-low",  f"📝 Score: {score}/10 — Needs Work"

        report_html = st.session_state.current_report.replace("\n", "<br>")
        report_placeholder.markdown(f"""
        <div class="report-card">
            <div class="score-badge {badge_cls}">{badge_label}</div>
            <div style="line-height:1.9; color:#e2e8f0;">
                {report_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Download buttons
        dl_col1, dl_col2, _ = st.columns([1, 1, 2])
        with dl_col1:
            st.download_button(
                label="📥 Download Markdown",
                data=st.session_state.current_report,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with dl_col2:
            try:
                import markdown
                from xhtml2pdf import pisa
                import io
                
                html = markdown.markdown(st.session_state.current_report)
                html_content = f"<html><head><style>body {{ font-family: Helvetica, sans-serif; font-size: 12px; line-height: 1.6; color: #333; }} h1, h2, h3 {{ color: #2c3e50; }} code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }} pre {{ background-color: #f4f4f4; padding: 10px; }}</style></head><body>{html}</body></html>"
                pdf_buf = io.BytesIO()
                pisa.CreatePDF(io.StringIO(html_content), dest=pdf_buf)
                pdf_bytes = pdf_buf.getvalue()

                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_bytes,
                    file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except ImportError:
                st.button("📄 PDF Exporting...", disabled=True, use_container_width=True)

render_report()


# ── Research Engine ────────────────────────────────────────────────────────────
def add_log(msg: str, agent: str = "system"):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append({"msg": msg, "agent": agent, "ts": ts})


def run_research_pipeline(query: str):
    """Run the LangGraph pipeline and update session state live."""
    try:
        # ── Apply sidebar settings to env ──
        os.environ["LLM_PROVIDER"]       = llm_provider
        os.environ["MAX_REVISIONS"]      = str(max_revisions)
        os.environ["QUALITY_THRESHOLD"]  = str(quality_threshold)
        if llm_provider == "groq":
            os.environ["GROQ_MODEL"]     = groq_model
        else:
            os.environ["OLLAMA_MODEL"]   = ollama_model

        model_display = groq_model if llm_provider == "groq" else ollama_model
        add_log("Initializing pipeline...", "system")
        add_log(f"Provider: {llm_provider.upper()} ({model_display})  |  Max revisions: {max_revisions}  |  Threshold: {quality_threshold}/10", "system")

        # ── Import here (so env vars are set first) ──
        import importlib
        import config as cfg
        importlib.reload(cfg)
        from graph.graph import build_graph

        # ── Planner ──
        st.session_state.agent_states["planner"] = "active"
        add_log("Planner is breaking your query into sub-tasks...", "planner")
        for agent in AGENTS:
            render_agent_card(agent_placeholders[agent["key"]], agent, st.session_state.agent_states[agent["key"]])
        render_logs()

        graph = build_graph()

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
            "max_revisions":  max_revisions,
            "final_report":   "",
        }

        # Stream through the graph node by node
        node_to_agent = {
            "planner":    "planner",
            "researcher": "researcher",
            "analyst":    "analyst",
            "writer":     "writer",
            "critic":     "critic",
        }

        log_messages = {
            "planner":    "Creating focused sub-tasks from your query...",
            "researcher": "Searching web + local knowledge base for each sub-task...",
            "analyst":    "Synthesizing all findings into key insights...",
            "writer":     "Writing the full research report...",
            "critic":     "Scoring and reviewing the report quality...",
        }

        prev_node = None
        current_state = initial_state.copy()

        for step in graph.stream(initial_state):
            node_name = list(step.keys())[0]
            state_update = step[node_name]
            
            # Merge partial state into our running state
            current_state.update(state_update)

            agent_key = node_to_agent.get(node_name, "system")

            # Mark previous node done
            if prev_node and prev_node in st.session_state.agent_states:
                st.session_state.agent_states[prev_node] = "done"

            # Mark current node active
            if agent_key in st.session_state.agent_states:
                st.session_state.agent_states[agent_key] = "active"

            add_log(log_messages.get(node_name, f"Running {node_name}..."), agent_key)

            # Extra detail logs
            if node_name == "planner" and "sub_tasks" in state_update:
                tasks = state_update["sub_tasks"]
                add_log(f"Created {len(tasks)} sub-tasks:", "planner")
                for i, t in enumerate(tasks, 1):
                    add_log(f"  {i}. {t}", "planner")

            elif node_name == "researcher":
                sr = state_update.get("search_results", [])
                rd = state_update.get("retrieved_docs", [])
                add_log(f"Web results: {len(sr)} | Local docs: {len(rd)}", "researcher")

            elif node_name == "writer":
                rev = state_update.get("revision_count", 1)
                add_log(f"Draft #{rev} written ({len(state_update.get('draft_report',''))} chars)", "writer")

            elif node_name == "critic":
                score = state_update.get("quality_score", 0)
                critique = state_update.get("critique", "")
                emoji = "✅" if score >= quality_threshold else "🔄"
                add_log(f"{emoji} Score: {score}/10 — {'Accepted!' if score >= quality_threshold else 'Requesting revision...'}", "critic")
                if score < quality_threshold:
                    add_log(f"Critique preview: {critique[:120]}...", "critic")

            # Update UI
            for agent in AGENTS:
                render_agent_card(agent_placeholders[agent["key"]], agent, st.session_state.agent_states[agent["key"]])
            render_logs()

            prev_node = agent_key

        # Mark all done
        for key in st.session_state.agent_states:
            st.session_state.agent_states[key] = "done"
        for agent in AGENTS:
            render_agent_card(agent_placeholders[agent["key"]], agent, st.session_state.agent_states[agent["key"]])

        # Extract final outputs directly from our accumulated state!
        report = current_state.get("final_report") or current_state.get("draft_report", "No report generated.")
        score  = current_state.get("quality_score", 0)
        revs   = current_state.get("revision_count", 0)

        st.session_state.current_report = report
        st.session_state.current_score  = score
        st.session_state.current_revs   = revs

        # Save to history
        st.session_state.history.append({
            "query":    query,
            "report":   report,
            "score":    score,
            "revisions": revs,
            "ts":       datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

        add_log(f"Research complete! Final score: {score}/10 after {revs} revision(s)", "system")
        render_logs()
        render_results()
        render_report()

        # Save report to outputs/
        Path("./outputs").mkdir(exist_ok=True)
        fname = f"./outputs/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"# Research Report\n\n**Query:** {query}\n\n**Score:** {score}/10\n\n---\n\n{report}")
        add_log(f"Report saved to {fname}", "system")
        render_logs()

    except Exception as e:
        add_log(f"ERROR: {str(e)}", "system")
        for key in st.session_state.agent_states:
            if st.session_state.agent_states[key] == "active":
                st.session_state.agent_states[key] = "error"
        for agent in AGENTS:
            render_agent_card(agent_placeholders[agent["key"]], agent, st.session_state.agent_states[agent["key"]])
        render_logs()
        st.session_state.error = str(e)

    finally:
        st.session_state.is_running = False


# ── Trigger Research ───────────────────────────────────────────────────────────
if run_btn and query and not st.session_state.is_running:
    # Reset state
    st.session_state.current_report = None
    st.session_state.current_score  = None
    st.session_state.current_revs   = None
    st.session_state.agent_states   = {n: "idle" for n in ["planner","researcher","analyst","writer","critic"]}
    st.session_state.logs           = []
    st.session_state.is_running     = True
    st.session_state.error          = None

    for agent in AGENTS:
        render_agent_card(agent_placeholders[agent["key"]], agent, "idle")

    with st.spinner("Research in progress... please wait."):
        run_research_pipeline(query)

    st.rerun()

elif run_btn and not query:
    st.warning("⚠️ Please enter a research question first!")


# ── Error Display ──────────────────────────────────────────────────────────────
if st.session_state.error:
    err = st.session_state.error

    # ── Smart error detection ──
    if "not found" in err.lower() and "404" in err:
        # Ollama model not downloaded
        st.markdown(f"""
        <div style='background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.4);
        border-radius:12px;padding:1.2rem;margin:1rem 0;'>
        <div style='color:#f87171;font-size:1rem;font-weight:600;margin-bottom:0.8rem;'>
        ❌ Model Not Found Error</div>
        <div style='color:#fca5a5;font-size:0.9rem;margin-bottom:1rem;'>
        The Ollama model <code style='color:#f87171;background:rgba(248,113,113,0.15);padding:2px 6px;border-radius:4px;'>{ollama_model}</code>
        is <b>not downloaded</b> on your machine yet!
        </div>
        <div style='color:#e2e8f0;font-size:0.88rem;'>
        <b>Fix:</b> Open your terminal and run:<br><br>
        <code style='color:#34d399;background:rgba(52,211,153,0.1);padding:6px 12px;border-radius:6px;display:block;margin:0.5rem 0;'>
        ollama pull {ollama_model}</code><br>
        Then refresh this page and try again.
        </div>
        </div>
        """, unsafe_allow_html=True)

    elif "groq_api_key" in err.lower() or "api key" in err.lower() or "authentication" in err.lower():
        st.markdown("""
        <div style='background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.4);
        border-radius:12px;padding:1.2rem;margin:1rem 0;'>
        <div style='color:#f87171;font-size:1rem;font-weight:600;margin-bottom:0.8rem;'>
        ❌ API Key Error</div>
        <div style='color:#fca5a5;font-size:0.9rem;'>
        Your <code>GROQ_API_KEY</code> is missing or invalid.<br><br>
        Check your <code>.env</code> file and make sure it contains a valid key.
        </div>
        </div>
        """, unsafe_allow_html=True)

    elif "connection" in err.lower() or "refused" in err.lower() or "11434" in err:
        st.markdown("""
        <div style='background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.4);
        border-radius:12px;padding:1.2rem;margin:1rem 0;'>
        <div style='color:#f87171;font-size:1rem;font-weight:600;margin-bottom:0.8rem;'>
        ❌ Ollama Not Running</div>
        <div style='color:#fca5a5;font-size:0.9rem;'>
        Cannot connect to Ollama at <code>localhost:11434</code>.<br><br>
        Make sure Ollama is installed and running, then try again.
        </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error(f"❌ **Error:** {err}")


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style='border-color:rgba(139,92,246,0.1); margin-top:3rem;'>
<div style='text-align:center; color:#334155; font-size:0.78rem; padding-bottom:1rem;'>
    🔬 Multi-Agent AI Research Assistant &nbsp;|&nbsp; LangGraph + Groq &nbsp;|&nbsp; Built with Streamlit
</div>
""", unsafe_allow_html=True)
