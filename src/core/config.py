# =============================================================================
# src/core/config.py — Application Configuration
# =============================================================================
# Context:
#   Single source of truth for all configurable parameters. Uses
#   pydantic-settings to load from environment variables and .env,
#   with sensible defaults so the app runs without any configuration.
#
# Architectural Reasoning:
#   - pydantic-settings over os.environ: validated types, aliases,
#     default values, and env_file support in one class. os.environ
#     is stringly-typed and has no validation.
#   - openai_kwargs / embedding_kwargs properties encapsulate the
#     LLM client construction logic. If a new AI provider is added,
#     only this class changes — every consumer uses the same kwargs.
#   - The USER_AGENT env var is set here (not in main.py) so it's
#     always configured before any HTTP client is constructed.
#
# Trade-offs:
#   - Flat config vs hierarchical. For portfolio scope, flat is fine.
#     In production with dozens of parameters, nested config classes
#     (e.g., Config.openai.model, Config.embedding.model) improve
#     discoverability.
#   - No secrets manager integration. In production, OPENAI_API_KEY
#     would come from Azure Key Vault / AWS Secrets Manager via a
#     custom pydantic validator, not .env.
#
# Opinionated Stance:
#   Hard-coded defaults for local development (no env file required)
#   with clear env-var override for production. Every new project
#   should start with pydantic-settings — it eliminates the "works
#   on my machine" class of config bugs.
# =============================================================================
from __future__ import annotations

import logging
import os
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    openai_api_key: str = Field(default="sk-placeholder", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: str = Field(default="", alias="OPENAI_BASE_URL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    agent_max_iterations: int = Field(default=5, alias="AGENT_MAX_ITERATIONS")

    @property
    def openai_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.openai_model,
            "temperature": 0.0,
            "max_tokens": 2048,
        }
        if self.openai_base_url:
            kwargs["base_url"] = self.openai_base_url
        if self.openai_api_key and self.openai_api_key != "sk-placeholder":
            kwargs["api_key"] = self.openai_api_key
        return kwargs

    @property
    def embedding_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"model": self.embedding_model}
        if self.openai_api_key and self.openai_api_key != "sk-placeholder":
            kwargs["api_key"] = self.openai_api_key
        if self.openai_base_url:
            kwargs["base_url"] = self.openai_base_url
        return kwargs

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

if not os.environ.get("USER_AGENT"):
    os.environ["USER_AGENT"] = "AgenticAIPlatform/1.0"
