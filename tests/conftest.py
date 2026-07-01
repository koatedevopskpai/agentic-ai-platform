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
