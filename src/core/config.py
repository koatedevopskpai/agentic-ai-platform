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
