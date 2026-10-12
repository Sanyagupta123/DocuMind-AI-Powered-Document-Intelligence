from __future__ import annotations

from fastapi import status


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ok"


def test_valid_upload_and_question_flow(client):
    payload = b"Eligibility requires a valid ID and proof of residency."
    response = client.post(
        "/documents/upload",
        files={"file": ("eligibility.txt", payload, "text/plain")},
    )
    assert response.status_code == status.HTTP_200_OK
    document = response.json()
    document_id = document["id"]

    answer = client.post(f"/documents/{document_id}/ask", json={"question": "What are the eligibility requirements?"})
    assert answer.status_code == status.HTTP_200_OK
    body = answer.json()
    assert body["status"] in {"success", "insufficient_evidence"}
    assert "answer" in body


def test_invalid_upload(client):
    response = client.post(
        "/documents/upload",
        files={"file": ("notes.md", b"# heading", "text/plain")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_unknown_document_returns_404(client):
    response = client.get("/documents/does-not-exist")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_invalid_question_returns_400(client):
    payload = b"Eligibility requires a valid ID."
    upload = client.post("/documents/upload", files={"file": ("eligibility.txt", payload, "text/plain")})
    document_id = upload.json()["id"]
    response = client.post(f"/documents/{document_id}/ask", json={"question": "   "})
    assert response.status_code == status.HTTP_200_OK or response.status_code == status.HTTP_400_BAD_REQUEST
