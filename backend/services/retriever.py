from __future__ import annotations

import re

from backend.config import settings
from backend.db.store import get_chunks_for_document
from backend.services.embeddings import LocalEmbeddingProvider, cosine_similarity


class InsufficientEvidenceError(ValueError):
    pass


SYNONYM_MAP = {
    "eligibility": {"eligibility", "eligible", "requirement", "requirements", "required", "proof", "residency", "applicant", "applicants", "qualify", "qualifies", "qualification", "qualified", "valid", "id"},
    "tuition": {"tuition", "assistance", "aid", "scholarship", "financial", "support"},
    "document": {"document", "policy", "criteria", "conditions", "rules"},
}


def _normalize_tokens(text: str) -> list[str]:
    cleaned = re.sub(r"[^a-z0-9]+", " ", (text or "").lower())
    tokens = [token.strip() for token in cleaned.split() if token.strip()]
    return [token[:-1] if len(token) > 3 and token.endswith("s") else token for token in tokens]


def _expand_tokens(text: str) -> set[str]:
    tokens = set(_normalize_tokens(text))
    expanded = set(tokens)
    for token in list(tokens):
        for group, variants in SYNONYM_MAP.items():
            if token == group or token in variants:
                expanded.update(variants)
                expanded.add(group)
    return expanded


def retrieve_document_chunks(document_id: str, question: str, limit: int | None = None, threshold: float | None = None) -> list[dict]:
    chunks = get_chunks_for_document(document_id)
    if not chunks:
        raise InsufficientEvidenceError("The document has no stored passages to search.")

    provider = LocalEmbeddingProvider()
    texts = [chunk["text"] for chunk in chunks]
    embeddings = provider.embed_many(texts)
    query_vector = provider.embed(question)
    question_tokens = _expand_tokens(question)
    scored: list[dict] = []

    for chunk, embedding in zip(chunks, embeddings):
        chunk_tokens = _expand_tokens(chunk["text"])
        overlap = len(question_tokens & chunk_tokens)
        lexical_score = overlap / max(1, len(question_tokens | chunk_tokens))
        cosine_score = cosine_similarity(embedding, query_vector)
        score = max(float(cosine_score), float(lexical_score) * 2.0)
        if score >= (threshold if threshold is not None else settings.relevance_threshold):
            scored.append({
                "id": chunk["id"],
                "text": chunk["text"],
                "page": chunk.get("page"),
                "score": float(score),
                "chunk_index": chunk.get("chunk_index"),
            })

    scored.sort(key=lambda item: item["score"], reverse=True)
    ordered = scored[: limit if limit is not None else settings.retrieval_limit]
    if not ordered:
        raise InsufficientEvidenceError("I could not find sufficient evidence in this document to support that answer.")
    return ordered
