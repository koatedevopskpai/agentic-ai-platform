# =============================================================================
# src/api/workflow.py — Workflow Execution Endpoint
# =============================================================================
# Context:
#   POST endpoint that accepts a task description and optional
#   max_iterations, executes the multi-agent reasoning loop,
#   and returns the full execution trace.
#
# Architectural Reasoning:
#   - Separate router file keeps route definitions out of main.py.
#     main.py only assembles the app; each domain owns its routes.
#   - Depends(get_agentic_workflow) resolves the singleton
#     service via the lru_cache DI pattern. No manual wiring.
#   - ValueError is caught and returned as 400. All other
#     exceptions propagate to FastAPI's error handler, ensuring
#     no unhandled crashes return raw tracebacks.
#   - Logging at INFO level records every execution for
#     observability. In production, structured JSON logging
#     would ship to a central log sink.
#
# Trade-offs:
#   - Synchronous handler in an async router. The agent loop is
#     CPU-bound (tool execution, LLM call), not I/O-bound. Making
#     it async wouldn't improve throughput without an async LLM
#     client and async tool implementations.
#
# Opinionated Stance:
#   Route handlers should be thin — validate input, delegate to
#   service, return result. Business logic never lives in routes.
# =============================================================================
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.core.dependencies import get_agentic_workflow
from src.models.agent import WorkflowRequest, WorkflowResponse
from src.services.agent_workflow import AgenticWorkflowService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/workflow", tags=["workflow"])


@router.post("/execute", response_model=WorkflowResponse)
async def execute_workflow(
    request: WorkflowRequest,
    workflow: AgenticWorkflowService = Depends(get_agentic_workflow),
) -> WorkflowResponse:
    try:
        result = workflow.execute(task=request.task, max_iterations=request.max_iterations)
        logger.info(
            "Workflow executed: %d steps, %dms, %d tokens",
            len(result.steps), result.total_duration_ms, result.total_tokens,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
