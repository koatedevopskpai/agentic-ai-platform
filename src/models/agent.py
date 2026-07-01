from __future__ import annotations

from pydantic import BaseModel, Field


class WorkflowRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=2000)
    max_iterations: int = Field(default=5, ge=1, le=20)


class ToolCallLog(BaseModel):
    tool: str
    input: str
    output: str
    duration_ms: int


class AgentStep(BaseModel):
    step: int
    thought: str
    tool_calls: list[ToolCallLog]


class WorkflowResponse(BaseModel):
    answer: str
    steps: list[AgentStep]
    total_tokens: int
    total_duration_ms: int
    model_used: str
