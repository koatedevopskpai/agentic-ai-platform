# Agentic AI Workflow Platform

[![CI](https://github.com/koatedevopskpai/agentic-ai-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/koatedevopskpai/agentic-ai-platform/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0%2B-1C3C3C)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> An **Agentic AI Workflow Platform** with a LangGraph-powered ReAct reasoning loop, tool-use execution, execution trace observability, and an interactive Streamlit dashboard. A reference implementation: typed, tested, containerised, and CI/CD-enabled.

---

## Why This Portfolio Exists

Most AI/LLM Engineer candidates can *describe* agent architectures. This portfolio *is* one. It demonstrates that I can build, test, containerise, and ship a functioning agentic system — not just configure one.

This platform proves I know:

- **Agentic Workflow Design** — ReAct (observe-think-act) reasoning loop with state management
- **LLM Integration** — ChatOpenAI with structured tool calling, token tracking, and cost observability
- **Tool Engineering** — Three production tools: math calculator, text analyzer, knowledge base retriever
- **Full-Stack AI** — FastAPI backend + Streamlit dashboard + Docker deployment
- **Software Engineering Rigour** — Typed, tested, containerised, CI/CD pipeline

---

## Features

| Feature | Description | Technology |
|---------|-------------|------------|
| **ReAct Agent Loop** | Observe-think-act cycle with configurable max iterations | LangGraph-style custom orchestrator |
| **Tool-Use Engine** | Agent calls tools (calculate, analyze, retrieve) during reasoning | LangChain `@tool` decorators |
| **Execution Trace** | Per-step thought + tool calls logged with timing and tokens | Pydantic models |
| **Streamlit Dashboard** | Visual agent interaction with metrics, traces, charts | Streamlit + Plotly |
| **Structured Logging** | Full observability: step, tool, token, and timing data | Python logging + pydantic |
| **Dockerised** | Single-container deployment with health checks | Docker + docker-compose |

---

## Architecture

```
                         ┌──────────────────────────────────┐
                         │       Streamlit Dashboard         │
                         │  (port 8501)                      │
                         │  Task Input · Trace Viewer ·      │
                         │  Metrics · Tool Usage Charts      │
                         └────────────┬─────────────────────┘
                                      │ HTTP (httpx)
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       FastAPI REST Layer                              │
│                                                                       │
│  POST /api/v1/workflow/execute ─── sends task ───► Agent Loop        │
│  GET  /api/v1/health            ─── liveness check                   │
└─────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  Agentic Workflow Service (Core Loop)                 │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────┐        │
│  │                    ReAct Reasoning Loop                    │        │
│  │                                                           │        │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────────────┐   │        │
│  │  │  Observe  │───▶│  Think   │───▶│  Act (Tool Call) │   │        │
│  │  └──────────┘    └──────────┘    └───────┬──────────┘   │        │
│  │         ▲                                 │              │        │
│  │         └─────────────────────────────────┘              │        │
│  │         (Loop until final answer or max iterations)      │        │
│  └──────────────────────────────────────────────────────────┘        │
│                                                                       │
│  Tool Registry:                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐       │
│  │  calculate() │  │ analyze_text│  │  knowledge_base()    │       │
│  │  (math eval) │  │ (text stats) │  │  (keyword retrieval) │       │
│  └──────────────┘  └──────────────┘  └──────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI + Uvicorn | Type-safe REST endpoints, auto OpenAPI docs |
| **Validation** | Pydantic v2 | Request/response schemas, runtime type enforcement |
| **Agent Framework** | LangGraph-style custom ReAct loop | Stateful agent orchestration |
| **LLM Integration** | LangChain + ChatOpenAI | OpenAI API with structured tool calling |
| **Tools** | LangChain `@tool` decorators | Calculator, text analyzer, knowledge base |
| **Dashboard** | Streamlit + Plotly | Interactive agent observability UI |
| **Configuration** | Pydantic Settings | Environment-based config, .env support |
| **Testing** | pytest + httpx | Unit tests, integration tests, mock LLM |
| **Container** | Docker + docker-compose | Single-service deployment |
| **CI/CD** | GitHub Actions | Automated test on push/PR |

---

## Quick Start

### Prerequisites

- Python 3.11+
- An OpenAI API key

### Installation

```bash
git clone https://github.com/koatedevopskpai/agentic-ai-platform.git
cd agentic-ai-platform

pip install .
```

### Run the API

```bash
export OPENAI_API_KEY="sk-..."
uvicorn src.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive Swagger UI.

### Run the Dashboard

```bash
streamlit run streamlit_app.py
```

Visit `http://localhost:8501`.

### Execute a Workflow (CLI)

```bash
curl -X POST http://localhost:8000/api/v1/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Calculate 15 * 24 + 7", "max_iterations": 5}'
```

Response includes the final answer plus a full execution trace (per-step thoughts, tool calls, durations, and token counts).

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Liveness check — returns status + version |
| POST | `/api/v1/workflow/execute` | Execute an agentic workflow with a task |

### Workflow Request

```json
{
  "task": "string (1-2000 chars)",
  "max_iterations": "integer (1-20, default: 5)"
}
```

### Workflow Response

```json
{
  "answer": "string (final response)",
  "steps": [
    {
      "step": 1,
      "thought": "I need to calculate this...",
      "tool_calls": [
        {
          "tool": "calculate",
          "input": "15 * 24 + 7",
          "output": "367",
          "duration_ms": 45
        }
      ]
    }
  ],
  "total_tokens": 1250,
  "total_duration_ms": 3200,
  "model_used": "gpt-4o-mini"
}
```

---

## Project Structure

```
agentic-ai-platform/
├── src/
│   ├── main.py                 # FastAPI app entry point (create_app factory)
│   ├── api/
│   │   ├── health.py           # GET /api/v1/health endpoint
│   │   └── workflow.py         # POST /api/v1/workflow/execute endpoint
│   ├── core/
│   │   ├── config.py           # Pydantic BaseSettings (env config)
│   │   └── dependencies.py     # FastAPI DI (lru_cache singletons)
│   ├── models/
│   │   └── agent.py            # Pydantic models: WorkflowRequest, WorkflowResponse, AgentStep, ToolCallLog
│   └── services/
│       ├── tools.py            # @tool functions: calculate, analyze_text, knowledge_base
│       └── agent_workflow.py   # ReAct reasoning loop (AgenticWorkflowService)
├── tests/
│   ├── conftest.py             # Mock LLM fixture + test app fixture
│   └── test_workflow.py        # Unit + integration tests (8 tests)
├── streamlit_app.py            # Streamlit dashboard with Plotly charts
├── Dockerfile                  # Single-stage Docker build
├── docker-compose.yml          # Container orchestration
├── .env.example                # Environment variable template
├── .github/workflows/ci.yml    # GitHub Actions CI pipeline
├── pyproject.toml              # Project metadata + dependencies
└── README.md                   # You are here
```

---

## Docker

```bash
# Build and run
docker compose up --build

# Or build manually
docker build -t agentic-ai-platform .
docker run -p 8000:8000 -e OPENAI_API_KEY="sk-..." agentic-ai-platform
```

The container includes a health check at `http://localhost:8000/api/v1/health`.

---

## Testing

```bash
# Run all tests with mock LLM
python -m pytest tests/ -v --tb=short

# Run with coverage
pip install pytest-cov
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Test Coverage

| Test | What It Validates |
|------|-------------------|
| `test_health_check` | API responds 200 with version |
| `test_workflow_execute` | Full workflow returns answer + steps + tokens + duration |
| `test_workflow_empty_task` | 422 validation on empty task |
| `test_workflow_tool_calls_tracked` | Every step has tool_calls list |
| `TestModels::test_tool_call_log` | ToolCallLog construction + validation |
| `TestModels::test_agent_step` | AgentStep construction with nested tool calls |
| `TestModels::test_workflow_response` | WorkflowResponse validation |
| `TestModels::test_workflow_request` | WorkflowRequest field validation |

All tests run with a deterministic mock LLM — no API key required, no external dependencies.

---

## Configuration

All configuration via environment variables (or `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | `sk-placeholder` | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | LLM model name |
| `OPENAI_BASE_URL` | `""` | For Azure OpenAI or local LLMs |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model (for future RAG) |
| `AGENT_MAX_ITERATIONS` | `5` | Default max reasoning steps |

---

## Tools

The agent has access to three tools during its reasoning loop:

### `calculate(expression: str)`
Evaluates mathematical expressions using a restricted `eval()` with whitelisted math functions. Returns the computed result.

### `analyze_text(text: str)`
Returns text statistics: word count, character count (with/without spaces), sentence count, estimated reading time, and unique word count.

### `knowledge_base(query: str)`
Keyword-matches against a curated knowledge base covering AI/LLM concepts: RAG, agent architectures, LangGraph, MCP, prompt engineering, vector databases, fine-tuning, and evaluation.

---

## Why This Matters for AI / LLM Engineer Roles

This portfolio directly demonstrates every skill an AI/LLM Engineer role requires:

1. **Agent Engineering** — Custom ReAct loop with state management, conditional routing, and iteration control
2. **LLM Integration** — OpenAI/ChatOpenAI with structured tool calling, token tracking, and cost observability
3. **Tool-Use Design** — Function calling with typed schemas, execution, and result integration
4. **Full-Stack Delivery** — Backend (FastAPI) + Frontend (Streamlit) + Containerisation (Docker) + CI/CD (GitHub Actions)
5. **Production Patterns** — Type hints, Pydantic validation, dependency injection, factory pattern, comprehensive testing
6. **Observability** — Per-step execution traces, timing metrics, token usage, structured logging
7. **Resilience** — Error handling at every layer, timeout controls, validation on all boundaries

---

## About the Author

**Koate Kpai, PMP, PRINCE2 Practitioner**

Eight years of enterprise data and platform engineering across regulated rail and utilities, now focused on AI engineering — combining that domain experience with typed, tested Python and modern agent frameworks.

- **Email:** koatekpai@outlook.com
- **GitHub:** [github.com/koatedevopskpai](https://github.com/koatedevopskpai)

---

## License

MIT
