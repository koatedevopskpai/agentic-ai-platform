from __future__ import annotations

from functools import lru_cache

from src.services.agent_workflow import AgenticWorkflowService


@lru_cache(maxsize=1)
def get_agentic_workflow() -> AgenticWorkflowService:
    return AgenticWorkflowService()
