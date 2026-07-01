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
