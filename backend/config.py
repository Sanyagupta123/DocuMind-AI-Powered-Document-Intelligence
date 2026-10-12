from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DocuMind"
    app_env: str = "development"
    database_url: str = "sqlite:///./documind.db"
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"])
    upload_max_size_mb: int = 10
    chunk_size: int = 500
    chunk_overlap: int = 80
    retrieval_limit: int = 5
    relevance_threshold: float = 0.1
    embedding_provider: str = "local"
    llm_provider: str = "local"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    frontend_api_base_url: str = "http://localhost:8000"
    project_root: str = str(Path(__file__).resolve().parents[2])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def upload_max_size_bytes(self) -> int:
        return self.upload_max_size_mb * 1024 * 1024

    @property
    def normalized_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins if origin and origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
