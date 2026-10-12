from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.db.store import get_document
from backend.schemas.models import QuestionRequest
from backend.services.rag import answer_question
from backend.services.retriever import InsufficientEvidenceError

router = APIRouter(prefix="/documents", tags=["questions"])


@router.post("/{document_id}/ask")
def ask_document_question(document_id: str, payload: QuestionRequest) -> dict:
    if not get_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found.")

    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="A question is required.")

    try:
        return answer_question(document_id, payload.question.strip())
    except InsufficientEvidenceError as exc:
        return {"answer": str(exc), "status": "insufficient_evidence", "sources": []}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive server error
        raise HTTPException(status_code=500, detail="Unable to answer the question at this time.") from exc
