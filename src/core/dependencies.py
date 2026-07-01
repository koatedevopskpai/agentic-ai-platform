# =============================================================================
# src/core/dependencies.py — FastAPI Dependency Injection
# =============================================================================
# Context:
#   Centralises FastAPI dependency providers so services are
#   instantiated once and shared across request handlers.
#
# Architectural Reasoning:
#   - lru_cache(maxsize=1) turns get_agentic_workflow into a
#     singleton factory. Every request gets the same instance
#     without global state or a DI framework.
#   - FastAPI's Depends() resolves the function, and lru_cache
#     ensures only one call to AgenticWorkflowService() ever
#     happens. This avoids re-initialising the LLM client on
#     every request.
#   - Testing: the cache is cleared in conftest.py before each
#     test to guarantee a fresh mock LLM. This pattern works
#     because lru_cache has a .cache_clear() method.
#
# Trade-offs:
#   - lru_cache vs FastAPI's request-scoped dependencies. For
#     singleton services, lru_cache is simpler than a custom
#     lifespan-managed container. If per-request state is ever
#     needed, the pattern must change to a factory per request.
#   - No async support. The workflow execute method is synchronous
#     (CPU-bound tool execution). If tools become I/O-bound, the
#     service and dependency would need async wrappers.
#
# Opinionated Stance:
#   lru_cache singletons are the least-overhead DI pattern for
#   FastAPI. No need for a container library when the standard
#   library does exactly what's needed.
# =============================================================================
from __future__ import annotations

from functools import lru_cache

from src.services.agent_workflow import AgenticWorkflowService


@lru_cache(maxsize=1)
def get_agentic_workflow() -> AgenticWorkflowService:
    return AgenticWorkflowService()
