from __future__ import annotations

from backend.db.store import save_document_record, save_chunks
from backend.services.rag import answer_question
from backend.services.retriever import InsufficientEvidenceError


def test_answer_includes_sources():
    document_id = "rag-doc"
    save_document_record(document_id, "policy.txt", "text/plain", 128, status="processed")
    save_chunks(document_id, [
        {"id": "a1", "index": 0, "text": "Eligibility requires proof of residency and a valid ID.", "page": 3, "embedding": []},
        {"id": "a2", "index": 1, "text": "Applicants can apply online or in person.", "page": 4, "embedding": []},
    ])
    result = answer_question(document_id, "What are the eligibility requirements?")
    assert result["status"] == "success"
    assert result["sources"]


def test_insufficient_evidence_case():
    document_id = "rag-empty"
    save_document_record(document_id, "policy.txt", "text/plain", 128, status="processed")
    save_chunks(document_id, [
        {"id": "b1", "index": 0, "text": "This document covers office hours and kiosk locations.", "page": 1, "embedding": []},
    ])
    try:
        answer_question(document_id, "Who qualifies for tuition assistance?")
        assert False, "Expected insufficient evidence error"
    except InsufficientEvidenceError:
        pass
