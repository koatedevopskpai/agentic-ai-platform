# =============================================================================
# src/api/health.py — Health Check Endpoint
# =============================================================================
# Context:
#   Liveness probe for container orchestrators and load balancers.
#   Returns 200 with version info — no downstream dependencies.
#
# Architectural Reasoning:
#   - No external dependency checking. A health check that fails
#     because the LLM API is unreachable creates false positives
#     during transient network issues. Liveness = process alive;
#     readiness = can serve traffic. This endpoint does liveness.
#   - Returns version so CI/CD can verify the correct deployment
#     is live before cutting over traffic.
#
# Trade-offs:
#   - Single endpoint for liveness + readiness. Kubernetes supports
#     both separately. For portfolio scope, one is sufficient.
#     In production, /health (liveness) and /ready (readiness with
#     DB/AI dependency checks) would be separate.
#
# Opinionated Stance:
#   Every web API needs a health check — it's table stakes for
#   production deployments. Keep it simple and stateless.
# =============================================================================
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}
