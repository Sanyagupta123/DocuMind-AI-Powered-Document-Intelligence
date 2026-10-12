from __future__ import annotations

from dataclasses import dataclass

from backend.config import settings


@dataclass
class Chunk:
    id: str
    index: int
    text: str
    page: int | None


def chunk_document(document_id: str, text: str, pages: list[str], chunk_size: int | None = None, overlap: int | None = None) -> list[Chunk]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")
    if overlap < 0:
        raise ValueError("chunk_overlap must be zero or greater.")
    if overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    cleaned = " ".join(part.strip() for part in text.split())
    if not cleaned:
        return []

    page_chunks: list[Chunk] = []
    for page_index, page_text in enumerate(pages, start=1):
        normalized = " ".join(part.strip() for part in page_text.split())
        if not normalized:
            continue
        words = normalized.split()
        step = chunk_size - overlap
        for start in range(0, len(words), step):
            segment = words[start : start + chunk_size]
            if not segment:
                continue
            chunk_text = " ".join(segment)
            if not chunk_text.strip():
                continue
            page_chunks.append(
                Chunk(
                    id=f"{document_id}-page-{page_index}-chunk-{len(page_chunks) + 1}",
                    index=len(page_chunks),
                    text=chunk_text,
                    page=page_index,
                )
            )
    if page_chunks:
        return page_chunks

    words = cleaned.split()
    step = chunk_size - overlap
    if step <= 0:
        step = max(1, chunk_size)
    result: list[Chunk] = []
    for start in range(0, len(words), step):
        segment = words[start : start + chunk_size]
        if not segment:
            continue
        text_blob = " ".join(segment)
        if text_blob.strip():
            result.append(
                Chunk(
                    id=f"{document_id}-chunk-{len(result) + 1}",
                    index=len(result),
                    text=text_blob,
                    page=None,
                )
            )
    return result
