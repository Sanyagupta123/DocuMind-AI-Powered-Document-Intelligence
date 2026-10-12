from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config import settings
from backend.db.store import (
    get_document,
    initialize_storage,
    list_documents,
    save_chunks,
    save_document_record,
    save_file_bytes,
    update_document_status,
)
from backend.services.chunker import chunk_document
from backend.services.document_parser import parse_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[dict])
def list_document_records() -> list[dict]:
    return list_documents()


@router.get("/{document_id}", response_model=dict)
def get_document_record(document_id: str) -> dict:
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@router.post("/upload", response_model=dict)
async def upload_document(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required.")

    filename = file.filename.lower()
    if not filename.endswith((".txt", ".pdf")):
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF or TXT file.")

    file_bytes = await file.read()
    if len(file_bytes) > settings.upload_max_size_bytes:
        raise HTTPException(status_code=413, detail=f"Upload exceeds the {settings.upload_max_size_mb} MB size limit.")

    document_id = str(uuid.uuid4())
    try:
        save_document_record(document_id, file.filename, file.content_type, len(file_bytes), status="processing")
        save_file_bytes(document_id, file_bytes, file.filename)
        parsed = parse_document(file.filename, file_bytes)
        chunks = chunk_document(document_id, parsed.text, parsed.pages)
        serialized_chunks = [
            {
                "id": chunk.id,
                "index": chunk.index,
                "text": chunk.text,
                "page": chunk.page,
                "embedding": [],
            }
            for chunk in chunks
        ]
        save_chunks(document_id, serialized_chunks)
        update_document_status(document_id, "processed")
        document = get_document(document_id)
        if document is None:
            raise HTTPException(status_code=500, detail="Document was uploaded but could not be retrieved.")
        return document
    except ValueError as exc:
        update_document_status(document_id, "failed", error_message=str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        update_document_status(document_id, "failed", error_message="An unexpected server error occurred while processing the document.")
        raise HTTPException(status_code=500, detail="An unexpected server error occurred while processing the document.") from exc
