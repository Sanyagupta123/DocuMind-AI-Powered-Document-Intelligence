from __future__ import annotations

from backend.db.store import save_document_record, save_chunks
from backend.services.retriever import retrieve_document_chunks


def test_retrieval_ranks_relevant_passages():
    document_id = "retrieval-doc"
    save_document_record(document_id, "policy.txt", "text/plain", 1024, status="processed")
    chunks = [
        {"id": "c1", "index": 0, "text": "Applicants must be over 18 and provide a valid government ID.", "page": 1, "embedding": []},
        {"id": "c2", "index": 1, "text": "The office hours are from 9am to 5pm Monday to Friday.", "page": 1, "embedding": []},
    ]
    save_chunks(document_id, chunks)
    results = retrieve_document_chunks(document_id, "What are the eligibility requirements?")
    assert results[0]["text"].lower().find("applicants") >= 0


def test_retrieval_handles_empty_document():
    try:
        retrieve_document_chunks("empty-doc", "What is this about?")
        assert False, "Expected InsufficientEvidenceError"
    except Exception as exc:
        assert "no stored passages" in str(exc).lower() or "insufficient" in str(exc).lower()
