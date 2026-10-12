from __future__ import annotations

from dataclasses import dataclass

import fitz


@dataclass
class DocumentContent:
    text: str
    pages: list[str]


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in value.split("\n")]
    return "\n".join(line for line in lines if line).strip()


def parse_document(filename: str, file_bytes: bytes) -> DocumentContent:
    name = (filename or "").lower()
    if name.endswith(".txt"):
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("utf-8", errors="ignore")
        normalized = normalize_text(text)
        if not normalized:
            raise ValueError("Uploaded text document is empty or contains no readable text.")
        return DocumentContent(text=normalized, pages=[normalized])

    if name.endswith(".pdf"):
        try:
            document = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as exc:  # pragma: no cover - parser failure path
            raise ValueError("PDF is corrupted or unreadable.") from exc

        pages: list[str] = []
        for page in document:
            page_text = page.get_text("text", sort=True).strip()
            if page_text:
                words = page_text.split()
                if words:
                    pages.append(page_text)
        if not pages:
            raise ValueError("PDF did not contain extractable text.")
        return DocumentContent(text="\n\n".join(pages), pages=pages)

    raise ValueError("Unsupported file type. Please upload a PDF or TXT file.")
