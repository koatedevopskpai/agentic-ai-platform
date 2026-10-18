# Evidence index — Agentic AI Platform

A reviewer's route through this repository. Every claim points at code, tests, or a dated
run recorded in [`evidence/`](evidence/). No claim is asserted without a location.

**Five-minute path:** this file → [what it is](#what-it-is) →
[the strongest measured result](#the-strongest-measured-result) →
[how to reproduce](#how-to-reproduce) →
[what this does not establish](#what-this-does-not-establish).

---

## What it is

A FastAPI agent-orchestration reference build. A ReAct-style loop (observe → think → act)
drives a small tool registry — `calculate`, `analyze_text`, `knowledge_base` — and every
step is captured as a Pydantic execution trace with tool calls, timing and tokens. A
Streamlit dashboard reads the same data for observability.

| | |
|---|---|
| Scope | **Public reference build.** Self-funded; no deployment, no hosted service |
| Author | Koate Kpai — https://github.com/koatedevopskpai |
| Entry point | `src/main.py`, `src/services/agent_workflow.py`, `streamlit_app.py` |
| Revision described | `0916eeb` |
| CI | **green** on `main`, 18 October 2026 |
| Evidence task | [`docs/V1.md`](docs/V1.md), [`evidence/V1.md`](evidence/V1.md) |

## My contribution

| Area | Source |
|---|---|
| ReAct loop with a configurable iteration cap | [`src/services/agent_workflow.py`](src/services/agent_workflow.py) |
| Tool registry — `calculate`, `analyze_text`, `knowledge_base` | [`src/services/tools.py`](src/services/tools.py) |
| Execution trace and API models | [`src/models/agent.py`](src/models/agent.py) |
| REST layer — `GET /api/v1/health`, `POST /api/v1/workflow/execute` | [`src/api/`](src/api/) |
| Observability dashboard | [`streamlit_app.py`](streamlit_app.py) |
| Test fixtures: a mock chat model and in-process ASGI transport | [`tests/conftest.py`](tests/conftest.py) |
| CI (install `.[dev]`, run the suite) | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |

---

## The strongest measured result

**8 tests, all passing — on Linux in CI and re-run locally.**

| Check | Linux CI (`main` @ `0916eeb`) | Windows local |
|---|---|---|
| `python -m pytest tests/ -v --tb=short` | **8 passed in 1.07s** | **8 passed in 3.25s** |

The tests exercise the app in-process over `ASGITransport` (no port binding):

| Test | What it establishes |
|---|---|
| `test_health_check` | `GET /health` returns 200 with version |
| `test_workflow_execute` | The workflow endpoint returns an answer, steps, tokens and a duration |
| `test_workflow_empty_task` | An empty task is rejected with **422**, not defaulted |
| `test_workflow_tool_calls_tracked` | Every step carries a `tool_calls` list |
| `TestModels` ×4 | The trace and response models construct and **validate** |

**What that result is worth.** It establishes that the loop's plumbing runs end to end,
that the endpoint contracts hold, and that bad input is refused. It establishes
**nothing** about how the agent behaves against a real model — see below.

### A claim that was corrected

The README previously published an `## About the Author` block naming a **different
person**, with a different email address, the retired `koate-kpai` account, and a
"20 years … £1.2B+ infrastructure programmes" claim that the CV contradicts (it states
**eight years**). It was replaced with the correct attribution, the account links were
repointed, and the deprecated "production-grade" framing was removed (commit `0916eeb`).
Correcting a claim downward is part of the evidence trail, not a footnote to it.

---

## How to reproduce

Offline and free — no provider key beyond a dummy, no network:

```bash
python -m venv .venv && . .venv/bin/activate
pip install ".[dev]"
python -m pytest tests/ -v --tb=short
```

CI additionally sets `OPENAI_API_KEY=sk-test-dummy`. The suite does **not** require it —
verified by running with the variable unset, which also gives **8 passed**. No provider is
contacted either way: `tests/conftest.py` replaces the chat client with a mock.

**Billable and not part of this evidence:** running against a real model, or starting the
Streamlit dashboard. Neither is recorded here.

---

## One success trace, one failure

**Success.** `test_workflow_execute` posts a task and receives a `WorkflowResponse` with
an answer, a list of steps, a token count and a duration — the whole loop running
in-process, with each step's tool calls recorded in the trace.

**Failure the API blocks.** `test_workflow_empty_task` sends an empty task and asserts
**422**. The service refuses rather than starting a loop on nothing. Rejecting input is
the correct outcome.

**The failure this suite cannot see.** No test makes a real model call. `tests/conftest.py`
substitutes a deterministic `MockChatOpenAI` that returns a tool call on its first
invocation and a final answer on its second. So a real model that ignores its tools,
loops without terminating, or returns a shape the parser rejects would **not** be caught
here. That is the honest boundary of this repository's evidence.

---

## Decisions and trade-offs

| Decision | Where |
|---|---|
| Mock the chat model at the import path rather than changing the service for testability | [`tests/conftest.py`](tests/conftest.py) |
| In-process `ASGITransport` instead of binding a port | [`tests/conftest.py`](tests/conftest.py) |
| Clear the service `lru_cache` after patching, so the singleton uses the mock | [`tests/conftest.py`](tests/conftest.py) |
| An explicit execution trace model rather than free-form logs | [`src/models/agent.py`](src/models/agent.py) |
| `dev` extra so CI can install the test tooling | [`pyproject.toml`](pyproject.toml) |

---

## What this does not establish

- **Agent quality.** No real model call is recorded anywhere. Tool selection, reasoning
  and answer quality are all unverified.
- **Tool correctness.** `calculate`, `analyze_text` and `knowledge_base` are not
  asserted to produce correct output; only that calls to them are traced.
- **The dashboard.** `streamlit_app.py` is never run in CI.
- **The container.** `Dockerfile` and `docker-compose.yml` exist but **CI does not build
  or run them**.
- **Lint.** CI runs **no linter at all** for this repository.
- **Production anything.** No deployment, uptime, customer or scale claim.

## Known weaknesses

- Coverage is **not measured** in CI; there is no gate and no recorded figure.
- CI has a **single job** — no lint, no image build, no compose smoke test.
- The suite is 8 tests in one file, and the mock is prescriptive: it dictates which tool
  is called, so the loop passes by construction rather than by judgement.
- CI sets a dummy `OPENAI_API_KEY` that the suite does not actually need — the variable
  is incidental to the run, which makes the workflow's environment slightly misleading.
