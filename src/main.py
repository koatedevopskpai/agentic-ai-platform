# =============================================================================
# src/main.py — FastAPI Application Entry Point
# =============================================================================
# Context:
#   Application factory and ASGI entry point. Assembles the FastAPI
#   app with CORS middleware and domain routers. The create_app()
#   factory pattern enables testing without side effects.
#
# Architectural Reasoning:
#   - create_app() factory over a module-level app: tests import
#     the factory and get a fresh app instance for each test. A
#     module-level app would be shared across tests, causing state
#     leakage.
#   - CORS middleware is configured permissively (allow_origins=["*"])
#     for local development. In production, this would restrict to
#     known frontend origins.
#   - Lifespan handler for startup/shutdown logging. No heavyweight
#     init (DB pools, AI model loading) in the lifespan because
#     the agent service is lazily instantiated via the DI container.
#   - Separate routers per domain (health, workflow). main.py only
#     wires; it doesn't define routes.
#
# Trade-offs:
#   - Factory function vs global app instance. The factory is
#     marginally more code but enables clean test isolation.
#     Worth the trade-off for testability.
#
# Opinionated Stance:
#   The factory pattern is non-negotiable for any FastAPI app that
#   has tests. A module-level `app = FastAPI()` creates a global
#   that can't be cleanly recreated between tests.
# =============================================================================
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.health import router as health_router
from src.api.workflow import router as workflow_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Agentic AI Platform starting up...")
    yield
    logger.info("Agentic AI Platform shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Agentic AI Workflow Platform",
        version="1.0.0",
        description="Multi-agent system with LangGraph, tool calling, and observability",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(workflow_router)

    return app


app = create_app()
