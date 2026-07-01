# =============================================================================
# tests/conftest.py — Test Fixtures and Mock LLM
# =============================================================================
# Context:
#   Shared test fixtures: mock LLM that replaces ChatOpenAI with a
#   deterministic stub, and an AsyncClient pointed at the test app
#   via ASGITransport (no HTTP server needed).
#
# Architectural Reasoning:
#   - MockChatOpenAI replaces ChatOpenAI at the import path level
#     (src.services.agent_workflow.ChatOpenAI). This means the
#     service code runs unmodified — no DI changes, no conditional
#     branches for testing. The mock returns tool calls on the
#     first invoke, then a final answer on the second.
#   - autouse fixture: every test automatically gets the mock LLM
#     without decoration. The conftest runs before test collection,
#     so the patch is active for all import-time code too.
#   - lru_cache is cleared after the patch is applied so the
#     singleton service is re-created with the mock LLM. Without
#     this, the first test caches the real LLM and subsequent
#     tests use it.
#   - ASGITransport avoids port binding. Tests run in-process,
#     no port conflicts, no server lifecycle. 100x faster than
#     spinning up a real uvicorn process.
#   - model_name is hardcoded to "mock-model" regardless of kwargs
#     so assertions in tests are deterministic.
#
# Trade-offs:
#   - Patch at class level vs instance level. Patching the class
#     means every ChatOpenAI() construction returns a MockChatOpenAI.
#     If a test needed a real LLM, it would need a nested patch or
#     a conditional mock. For portfolio scope, 100% mock coverage
#     is acceptable.
#
# Opinionated Stance:
#   Mock at the import boundary, not via DI injection. Patching
#   ChatOpenAI at the module level tests the real code path without
#   test-specific branches. The only thing we lose is the ability
#   to test real LLM calls — which we don't want in unit tests
#   anyway.
# =============================================================================
from __future__ import annotations

import os
from unittest.mock import patch, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy")


class MockChatOpenAI:
    """Mock that returns tool calls then a final answer for agent tests."""

    def __init__(self, **kwargs):
        self.model_name = "mock-model"
        self._call_count = 0

    def invoke(self, messages, **kwargs):
        from langchain_core.messages import AIMessage

        self._call_count += 1

        if self._call_count == 1:
            return AIMessage(
                content="I need to calculate the square root of 144 first.",
                tool_calls=[
                    {"id": "call_1", "name": "calculate", "args": {"expression": "math.sqrt(144)"}},
                ],
            )
        elif self._call_count == 2:
            return AIMessage(
                content="The result is 12.0. Now I have the answer.",
                tool_calls=[],
            )
        return AIMessage(content="Mocked final answer.")

    def bind_tools(self, tools, **kwargs):
        return self

    __call__ = invoke


@pytest.fixture(autouse=True)
def mock_llm():
    patcher = patch("src.services.agent_workflow.ChatOpenAI", MockChatOpenAI)
    mock = patcher.start()

    from src.core import dependencies as deps
    deps.get_agentic_workflow.cache_clear()

    yield mock

    patcher.stop()


@pytest.fixture
async def test_app() -> AsyncClient:
    from src.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
