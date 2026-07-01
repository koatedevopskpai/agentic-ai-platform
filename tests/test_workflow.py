# =============================================================================
# tests/test_workflow.py — API and Model Unit Tests
# =============================================================================
# Context:
#   Tests for the workflow API endpoint and all Pydantic models.
#   Covers: health check, workflow execution, input validation,
#   model serialisation, and tool call tracking.
#
# Architectural Reasoning:
#   - API tests use the test_app fixture (AsyncClient + ASGITransport)
#     so they exercise the full FastAPI stack — middleware, route
#     handlers, validation, dependency injection — without HTTP.
#   - Model tests are pure Pydantic unit tests. No fixtures needed,
#     no async. They verify serialisation and validation logic in
#     isolation from the service layer.
#   - test_workflow_execute verifies the full agent cycle: POST
#     with a task, then asserts answer length, step count, token
#     tracking, duration, and model name. The mock LLM guarantees
#     deterministic output.
#   - test_workflow_empty_task verifies FastAPI's built-in validation
#     rejects empty tasks (422). This is a contract test — the client
#     must know that empty tasks are rejected before they reach the
#     service.
#   - test_workflow_tool_calls_tracked ensures every step has a
#     tool_calls list (even if empty). The response schema guarantees
#     this, but the test proves it works end-to-end.
#
# Trade-offs:
#   - One test file for everything vs separate files per domain.
#     With 8 tests in one file, navigation is easy. As the test
#     suite grows, splitting by domain (test_api/, test_models/)
#     keeps CI runs parallel.
#   - End-to-end API tests vs unit tests for the service. The API
#     tests cover the service via integration. Pure service unit
#     tests would mock the LLM at a lower level for finer-grained
#     assertions. For portfolio scope, API-level tests provide
#     better confidence with fewer tests.
#
# Opinionated Stance:
#   Test at the API boundary, not the service layer. If the API
#   response is correct, the service is correct. This reduces test
#   fragility from internal refactors.
# =============================================================================
from __future__ import annotations

import pytest
from httpx import AsyncClient

from src.models.agent import ToolCallLog, AgentStep, WorkflowResponse, WorkflowRequest


@pytest.mark.asyncio
async def test_health_check(test_app: AsyncClient) -> None:
    resp = await test_app.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_workflow_execute(test_app: AsyncClient) -> None:
    resp = await test_app.post(
        "/api/v1/workflow/execute",
        json={"task": "Calculate the square root of 144.", "max_iterations": 5},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["answer"]) > 0
    assert len(data["steps"]) > 0
    assert data["total_tokens"] >= 0
    assert data["total_duration_ms"] >= 0
    assert data["model_used"] == "mock-model"


@pytest.mark.asyncio
async def test_workflow_empty_task(test_app: AsyncClient) -> None:
    resp = await test_app.post(
        "/api/v1/workflow/execute",
        json={"task": "", "max_iterations": 5},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_workflow_tool_calls_tracked(test_app: AsyncClient) -> None:
    resp = await test_app.post(
        "/api/v1/workflow/execute",
        json={"task": "Calculate 2 + 2", "max_iterations": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    for step in data["steps"]:
        assert "step" in step
        assert "thought" in step
        assert "tool_calls" in step


class TestModels:
    def test_tool_call_log(self) -> None:
        tcl = ToolCallLog(tool="calculate", input='{"expression": "2+2"}', output="4", duration_ms=50)
        assert tcl.tool == "calculate"
        assert tcl.duration_ms == 50

    def test_agent_step(self) -> None:
        tcl = ToolCallLog(tool="calc", input="{}", output="4", duration_ms=10)
        step = AgentStep(step=1, thought="I need to calculate", tool_calls=[tcl])
        assert step.step == 1
        assert len(step.tool_calls) == 1

    def test_workflow_response(self) -> None:
        resp = WorkflowResponse(answer="42", steps=[], total_tokens=10, total_duration_ms=100, model_used="test")
        assert resp.answer == "42"
        assert resp.total_tokens == 10

    def test_workflow_request_validation(self) -> None:
        with pytest.raises(Exception):
            WorkflowRequest(task="", max_iterations=5)
