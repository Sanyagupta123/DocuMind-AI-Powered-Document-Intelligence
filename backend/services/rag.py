from __future__ import annotations

from backend.services.retriever import InsufficientEvidenceError, retrieve_document_chunks


class GroundedAnswerResult(dict):
    pass


def _best_sentence(text: str) -> str:
    normalized = " ".join(text.split())
    sentences = [part.strip() for part in normalized.replace("?", ".").replace("!", ".").split(".") if part.strip()]
    if not sentences:
        return normalized[:220]
    return sentences[0][:220]


def answer_question(document_id: str, question: str) -> dict:
    hits = retrieve_document_chunks(document_id, question)
    if not hits:
        raise InsufficientEvidenceError("I could not find sufficient evidence in this document to support that answer.")

    best_hit = hits[0]
    answer = _best_sentence(best_hit["text"])
    if question.lower().startswith(("what", "who", "when", "where", "why", "how")):
        answer = answer if answer.endswith((".", "!", "?")) else answer + "."
    else:
        answer = f"Based on the document, {answer}"

    return {
        "answer": answer,
        "status": "success",
        "sources": [
            {
                "index": index,
                "page": hit.get("page"),
                "text": hit["text"],
                "score": round(hit["score"], 4),
            }
            for index, hit in enumerate(hits, start=1)
        ],
    }
