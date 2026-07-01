from __future__ import annotations

import json
import logging
import time
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from src.core.config import settings
from src.models.agent import AgentStep, ToolCallLog, WorkflowResponse
from src.services.tools import TOOL_MAP, run_tool

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI agent that solves tasks by using tools. Follow this reasoning loop:

1. THINK about what the task requires
2. DECIDE which tool to call (if needed) with the correct arguments
3. CALL the tool using the function calling format
4. OBSERVE the tool output
5. REPEAT until the task is complete, then provide your final answer

Available tools:
- calculate(expression: str) — Evaluate a mathematical expression
- analyze_text(text: str) — Get statistics about a piece of text
- knowledge_base(query: str) — Search the internal knowledge base for information

Rules:
- Always call a tool when you need information or computation
- You can call multiple tools in sequence
- When you have enough information, provide a clear final answer
- If you cannot complete the task, explain what is missing"""


class AgenticWorkflowService:
    def __init__(self) -> None:
        self._llm = ChatOpenAI(**settings.openai_kwargs)
        self._max_iterations = settings.agent_max_iterations
        logger.info("Initialized AgenticWorkflowService with model=%s", settings.openai_model)

    def execute(self, task: str, max_iterations: int | None = None) -> WorkflowResponse:
        iterations = max_iterations or self._max_iterations
        messages: list[Any] = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=task),
        ]

        steps: list[AgentStep] = []
        total_duration = 0
        total_tokens = 0
        final_answer = ""

        for step_num in range(iterations):
            step_start = time.monotonic()

            llm_response = self._llm.invoke(messages)
            usage = getattr(llm_response, "usage_metadata", None)
            total_tokens += usage.get("total_tokens", 0) if usage else 0

            messages.append(llm_response)
            content = str(llm_response.content)

            tool_calls = getattr(llm_response, "tool_calls", []) or []
            if isinstance(tool_calls, list) and len(tool_calls) > 0:
                tool_logs: list[ToolCallLog] = []

                for tc in tool_calls:
                    tc_id = tc.get("id", "") if isinstance(tc, dict) else getattr(tc, "id", "")
                    tc_name = tc.get("name", "") if isinstance(tc, dict) else getattr(tc, "name", "")
                    tc_args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {})

                    tool_start = time.monotonic()
                    output = run_tool(tc_name, tc_args)
                    tool_duration = int((time.monotonic() - tool_start) * 1000)

                    tool_logs.append(ToolCallLog(
                        tool=tc_name,
                        input=json.dumps(tc_args),
                        output=str(output)[:300],
                        duration_ms=tool_duration,
                    ))

                    messages.append(ToolMessage(content=str(output), tool_call_id=tc_id))

                step_duration = int((time.monotonic() - step_start) * 1000)
                total_duration += step_duration

                steps.append(AgentStep(
                    step=step_num + 1,
                    thought=content[:500],
                    tool_calls=tool_logs,
                ))
            else:
                step_duration = int((time.monotonic() - step_start) * 1000)
                total_duration += step_duration

                steps.append(AgentStep(
                    step=step_num + 1,
                    thought=content[:500],
                    tool_calls=[],
                ))
                final_answer = content
                break
        else:
            final_answer = "Task completed after reaching maximum iterations."

        if not final_answer:
            final_answer = content if "content" in dir(locals().get("llm_response", {})) else "No final answer generated."

        return WorkflowResponse(
            answer=final_answer,
            steps=steps,
            total_tokens=total_tokens,
            total_duration_ms=total_duration,
            model_used=getattr(self._llm, "model_name", settings.openai_model),
        )
