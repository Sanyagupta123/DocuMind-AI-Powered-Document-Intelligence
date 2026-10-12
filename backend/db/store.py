from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import settings

PROJECT_ROOT = Path(settings.project_root)
UPLOAD_DIR = PROJECT_ROOT / "uploads"
DB_PATH = PROJECT_ROOT / "documind.db"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_storage() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                content_type TEXT,
                size_bytes INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                file_path TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                page INTEGER,
                embedding TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(document_id) REFERENCES documents(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def list_documents() -> list[dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM documents ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_document(document_id: str) -> dict[str, Any] | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def save_document_record(document_id: str, filename: str, content_type: str | None, size_bytes: int, status: str = "uploaded") -> dict[str, Any]:
    now = _now_iso()
    metadata = json.dumps({"filename": filename}, ensure_ascii=False)
    conn = _connect()
    try:
        conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
        conn.execute(
            """
            INSERT OR REPLACE INTO documents (id, filename, content_type, size_bytes, status, created_at, updated_at, metadata, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (document_id, filename, content_type, size_bytes, status, now, now, metadata, None),
        )
        conn.commit()
        return get_document(document_id) or {}
    finally:
        conn.close()


def update_document_status(document_id: str, status: str, metadata: dict[str, Any] | None = None, error_message: str | None = None) -> None:
    now = _now_iso()
    conn = _connect()
    try:
        row = conn.execute("SELECT metadata FROM documents WHERE id = ?", (document_id,)).fetchone()
        payload = json.loads(row["metadata"]) if row and row["metadata"] else {}
        if metadata:
            payload.update(metadata)
        if error_message:
            payload["error"] = error_message
        conn.execute(
            "UPDATE documents SET status = ?, updated_at = ?, metadata = ? WHERE id = ?",
            (status, now, json.dumps(payload, ensure_ascii=False), document_id),
        )
        conn.commit()
    finally:
        conn.close()


def set_document_file_path(document_id: str, file_path: str) -> None:
    conn = _connect()
    try:
        conn.execute("UPDATE documents SET file_path = ? WHERE id = ?", (file_path, document_id))
        conn.commit()
    finally:
        conn.close()


def save_file_bytes(document_id: str, file_bytes: bytes, original_filename: str) -> str:
    safe_name = f"{document_id}_{original_filename.replace('/', '_').replace('\\', '_')}"
    destination = UPLOAD_DIR / safe_name
    destination.write_bytes(file_bytes)
    set_document_file_path(document_id, str(destination))
    return str(destination)


def save_chunks(document_id: str, chunks: list[dict[str, Any]]) -> None:
    conn = _connect()
    try:
        for chunk in chunks:
            conn.execute(
                """
                INSERT INTO chunks (id, document_id, chunk_index, text, page, embedding, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk["id"],
                    document_id,
                    chunk["index"],
                    chunk["text"],
                    chunk.get("page"),
                    json.dumps(chunk.get("embedding", []), ensure_ascii=False),
                    _now_iso(),
                ),
            )
        conn.commit()
    finally:
        conn.close()


def get_chunks_for_document(document_id: str) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM chunks WHERE document_id = ? ORDER BY chunk_index ASC",
            (document_id,),
        ).fetchall()
        chunks: list[dict[str, Any]] = []
        for row in rows:
            payload = dict(row)
            payload["embedding"] = json.loads(payload["embedding"]) if payload["embedding"] else []
            chunks.append(payload)
        return chunks
    finally:
        conn.close()


def cleanup_document(document_id: str) -> None:
    conn = _connect()
    try:
        conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
        conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        conn.commit()
    finally:
        conn.close()
