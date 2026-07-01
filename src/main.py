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
