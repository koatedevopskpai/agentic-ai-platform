# =============================================================================
# streamlit_app.py — Agent Observability Dashboard
# =============================================================================
# Context:
#   Streamlit frontend for the Agentic AI Workflow Platform. Provides
#   a chat-like interface to submit tasks, view the agent's reasoning
#   trace step by step, and inspect metrics (tokens, duration, tool
#   calls per step).
#
# Architectural Reasoning:
#   - Streamlit over a custom React frontend: zero frontend build
#     tooling, automatic dark/light theme, and native charting via
#     Plotly. Streamlit apps are single-file Python scripts — ideal
#     for portfolio demos where frontend is not the focus.
#   - httpx to talk to the FastAPI backend. Synchronous requests are
#     fine in Streamlit because the UI blocks on execution anyway.
#   - st.columns + st.metric for summary KPIs. st.expander for
#     each step's trace — steps are collapsible so the user can
#     focus on one step at a time.
#   - Plotly bar chart for tool calls per step: converts the trace
#     to a pandas DataFrame in one line. Quick visual signal on
#     where the agent spent its tool budget.
#   - Example task buttons with st.session_state rerun pattern:
#     clicking a button sets the task text and triggers a rerun so
#     the user can edit before executing.
#
# Trade-offs:
#   - Streamlit vs Gradio vs full React. Streamlit is the fastest
#     path to a working dashboard. Gradio would be better for
#     demo-sharing (public links). React for production UX. For
#     portfolio, Streamlit shows full-stack capability without
#     the complexity of a JS framework.
#   - Synchronous httpx vs async. Streamlit's execution model is
#     synchronous per rerun — there's no benefit to async here.
#
# Opinionated Stance:
#   Every backend needs a frontend, even if it's a Streamlit
#   dashboard. Visualising the agent's reasoning trace is the
#   single most important feature for debugging and demoing
#   agentic systems.
# =============================================================================
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
import httpx

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Agentic AI Platform", layout="wide")
st.title("Agentic AI Workflow Platform")
st.markdown("Multi-agent system with tool calling, reasoning traces, and observability")

cola, colb = st.columns([3, 1])
with cola:
    task = st.text_area(
        "Task Description",
        value="Calculate the square root of 144 and then analyze this text: 'Agentic AI systems use tools to solve complex problems by reasoning step by step.'",
        height=100,
    )
with colb:
    max_iter = st.slider("Max Iterations", 1, 10, 5)
    run_btn = st.button("Execute Workflow", type="primary", use_container_width=True)

if run_btn and task:
    with st.spinner("Agent is thinking and calling tools..."):
        try:
            resp = httpx.post(
                f"{API_URL}/workflow/execute",
                json={"task": task, "max_iterations": max_iter},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            st.error(f"API error: {e}")
            data = None

    if data:
        st.success("Workflow completed")

        metrics_cols = st.columns(4)
        metrics_cols[0].metric("Steps", len(data["steps"]))
        metrics_cols[1].metric("Duration", f"{data['total_duration_ms']}ms")
        metrics_cols[2].metric("Tokens", data["total_tokens"])
        metrics_cols[3].metric("Model", data["model_used"])

        st.subheader("Final Answer")
        st.markdown(data["answer"])

        st.subheader("Agent Execution Trace")
        for step in data["steps"]:
            with st.expander(f"Step {step['step']} — {len(step['tool_calls'])} tool call(s)"):
                st.markdown("**Thought:**")
                st.write(step["thought"])

                if step["tool_calls"]:
                    st.markdown("**Tool Calls:**")
                    for tc in step["tool_calls"]:
                        cols = st.columns([1, 2, 2, 1])
                        cols[0].markdown(f"**{tc['tool']}**")
                        cols[1].code(tc["input"], language="json")
                        cols[2].write(tc["output"][:200])
                        cols[3].caption(f"{tc['duration_ms']}ms")

        st.subheader("Metrics")
        df = pd.DataFrame([
            {"step": s["step"], "tool_calls": len(s["tool_calls"]), "thought_len": len(s["thought"])}
            for s in data["steps"]
        ])
        if not df.empty:
            fig = px.bar(df, x="step", y="tool_calls", title="Tool Calls per Step", labels={"step": "Step", "tool_calls": "Tool Calls"})
            st.plotly_chart(fig, use_container_width=True)

elif run_btn and not task:
    st.warning("Please enter a task description.")

st.divider()
st.subheader("Example Tasks")
examples = [
    "Calculate 15 * 23 + 42 and then find the square root of the result.",
    "What is an AI agent? Explain how LangGraph helps build them.",
    "Analyze this text: 'RAG systems combine retrieval with generation to produce grounded answers. They reduce hallucination and enable knowledge updates without retraining.'",
    "What is the Model Context Protocol (MCP) and how does it relate to agent tool calling?",
]
for ex in examples:
    if st.button(ex, use_container_width=True):
        st.session_state.task = ex
        st.rerun()
