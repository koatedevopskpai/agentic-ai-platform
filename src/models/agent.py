# =============================================================================
# src/models/agent.py — Agent Data Models
# =============================================================================
# Context:
#   Pydantic models for the agentic workflow API: request/response
#   contracts and the internal step/tool-call log types.
#
# Architectural Reasoning:
#   - Separate request (WorkflowRequest) from response
#     (WorkflowResponse) models. This allows the request schema
#     to evolve independently (e.g., adding optional fields) without
#     breaking existing clients parsing the response.
#   - ToolCallLog and AgentStep are nested within the response.
#     Nesting rather than flattening makes the trace structure
#     self-documenting: each step owns its tool calls.
#   - Field validation (min_length, ge/le) catches bad input at
#     the API boundary before the service layer is invoked.
#
# Trade-offs:
#   - All models in one file vs one file per model. For five small
#     models, a single file is easier to navigate. If models grew
#     to 20+, they should be split by domain.
#   - No discriminated unions for tool types. If tools had different
#     input schemas, a Union type per tool would be warranted.
#
# Opinionated Stance:
#   Pydantic v2 models are the interface contract. Every field gets
#   validation. No model is shared between request and response —
#   that coupling causes breaking changes.
# =============================================================================
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
