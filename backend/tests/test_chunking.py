from __future__ import annotations

from backend.services.chunker import chunk_document


def test_chunk_short_document():
    chunks = chunk_document("doc-1", "This is a short document about eligibility.", ["This is a short document about eligibility."], chunk_size=25, overlap=5)
    assert chunks
    assert all(chunk.text for chunk in chunks)


def test_chunk_long_document_has_overlap():
    text = " ".join([f"token-{index}" for index in range(200)])
    chunks = chunk_document("doc-2", text, [text], chunk_size=20, overlap=5)
    assert len(chunks) > 1
    assert chunks[0].text != chunks[1].text


def test_chunk_document_preserves_page_metadata():
    page_text = "Page one contains eligibility criteria. Page two has application steps."
    chunks = chunk_document("doc-3", page_text, [page_text], chunk_size=10, overlap=2)
    assert all(chunk.page == 1 for chunk in chunks)
