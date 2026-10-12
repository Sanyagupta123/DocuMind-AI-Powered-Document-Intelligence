from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.documents import router as documents_router
from backend.api.health import router as health_router
from backend.api.questions import router as questions_router
from backend.config import settings
from backend.db.store import initialize_storage

app = FastAPI(
    title="DocuMind",
    description="AI-powered document intelligence built for local document search and grounded answers.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.normalized_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(documents_router)
app.include_router(questions_router)


@app.on_event("startup")
def startup() -> None:
    initialize_storage()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
