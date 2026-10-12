from __future__ import annotations

import fitz

from backend.services.document_parser import parse_document


def test_parse_txt_document():
    payload = b"Eligibility requires a valid ID and residency proof.\n"
    content = parse_document("sample.txt", payload)
    assert "Eligibility" in content.text
    assert len(content.pages) == 1


def test_parse_pdf_document():
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "This is an eligibility policy document.")
    buffer = __import__('io').BytesIO()
    document.save(buffer, garbage=0)
    pdf_bytes = buffer.getvalue()
    document.close()
    content = parse_document("sample.pdf", pdf_bytes)
    assert "eligibility" in content.text.lower()
    assert content.pages


def test_parse_empty_text_document():
    try:
        parse_document("empty.txt", b"\n \t\r\n")
        assert False, "Expected ValueError for empty text"
    except ValueError as exc:
        assert "empty" in str(exc).lower()


def test_parse_corrupt_pdf_document():
    try:
        parse_document("broken.pdf", b"not a real pdf")
        assert False, "Expected ValueError for corrupt PDF"
    except ValueError as exc:
        assert "corrupt" in str(exc).lower() or "unreadable" in str(exc).lower()


def test_parse_unsupported_file():
    try:
        parse_document("notes.md", b"# Heading")
        assert False, "Expected ValueError for unsupported type"
    except ValueError as exc:
        assert "unsupported" in str(exc).lower()
