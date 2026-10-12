# DocuMind

DocuMind is a lightweight AI-powered document intelligence application for uploading PDF and TXT files, extracting text, chunking passages, and asking grounded questions about the content. It retrieves the most relevant document passages and returns concise answers with source references that can be inspected in context.

## Problem statement

Document-heavy teams often need to quickly answer specific questions from long policy documents, manuals, and research notes. Without a retrieval layer, generic chat responses can hallucinate or omit evidence. DocuMind adds a small RAG workflow that keeps answers grounded in the uploaded document.

## Main features

- Upload PDF or TXT files
- Parse and validate readable content
- Chunk text with overlap, preserving page metadata when available
- Store and query document passages locally
- Ask grounded questions scoped to the selected document
- Retrieve passage evidence and show numbered source references
- Display insufficient-evidence responses when the document does not support the answer
- Modern light-theme dashboard for document management and Q&A

## Architecture overview

```text
React frontend
  -> FastAPI API
  -> document parser
  -> chunker
  -> local embedding / retrieval layer
  -> answer generation with evidence references
```

## Tech stack

- FastAPI
- Pydantic + Python 3.12
- PyMuPDF for PDF extraction
- scikit-learn based local embedding provider
- SQLite for the local MVP storage
- React + Vite + TypeScript
- Pytest for backend validation

## Repository structure

```text
backend/
  api/
  db/
  services/
  tests/
  config.py
  main.py
  requirements.txt
frontend/
  src/
  package.json
README.md
.env.example
.gitignore
docker-compose.yml
.github/workflows/ci.yml
```

## Prerequisites

- Python 3.12
- Node.js 20+
- npm
- Docker (optional for local Postgres)

## Setup

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows PowerShell
```

2. Install the backend dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Install the frontend dependencies:

```bash
cd frontend
npm install
```

4. Copy the sample environment file and review the values:

```bash
copy .env.example .env
```

## Running the app

### Backend

```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

Open http://localhost:5173 to use the application.

## Environment variables

The project uses the following variables:

- `APP_ENV`
- `DATABASE_URL`
- `CORS_ORIGINS`
- `UPLOAD_MAX_SIZE_MB`
- `CHUNK_SIZE`
- `CHUNK_OVERLAP`
- `RETRIEVAL_LIMIT`
- `RELEVANCE_THRESHOLD`
- `FRONTEND_API_BASE_URL`

See `.env.example` for the default values.

## Testing

Run the backend suite:

```bash
source .venv/bin/activate
pytest backend/tests -q
```

Build the frontend:

```bash
cd frontend
npm run build
```

## Docker Compose

A minimal Compose file is included for local PostgreSQL if you need a service-backed database. It is optional for this MVP because the default configuration uses SQLite.

```bash
docker compose up -d
```

## Notes

This app intentionally keeps the MVP small and local-first. It avoids external paid AI services by default and uses a local embedding approach suitable for development and demos. If you later switch to a hosted embedding or LLM provider, you can add the provider configuration in the backend settings and environment file.
