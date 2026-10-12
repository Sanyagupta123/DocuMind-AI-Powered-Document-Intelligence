from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


class DocumentSummary(BaseModel):
    id: str
    filename: str
    content_type: str | None = None
    size_bytes: int
    status: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class SourceReference(BaseModel):
    index: int
    page: int | None = None
    text: str
    score: float | None = None


class QuestionResponse(BaseModel):
    answer: str
    status: str
    sources: list[SourceReference]
