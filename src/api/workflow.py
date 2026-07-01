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
