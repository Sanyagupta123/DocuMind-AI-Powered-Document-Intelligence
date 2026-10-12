import { type ChangeEvent, type FormEvent, useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000'

type DocumentItem = {
  id: string
  filename: string
  size_bytes: number
  status: string
  created_at: string
  updated_at: string
  metadata?: Record<string, unknown>
  content_type?: string
}

type SourceReference = {
  index: number
  page: number | null
  text: string
  score?: number
}

type AnswerResult = {
  answer: string
  status: string
  sources: SourceReference[]
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options)
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = typeof data.detail === 'string' ? data.detail : 'Request failed.'
    throw new Error(message)
  }
  return data as T
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  const units = ['KB', 'MB', 'GB']
  let size = bytes / 1024
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex += 1
  }
  return `${size.toFixed(size >= 10 ? 0 : 1)} ${units[unitIndex]}`
}

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Unknown date'
  return date.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
}

function App() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [selectedDocumentId, setSelectedDocumentId] = useState('')
  const [uploading, setUploading] = useState(false)
  const [question, setQuestion] = useState('')
  const [questionLoading, setQuestionLoading] = useState(false)
  const [loadingDocuments, setLoadingDocuments] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [answer, setAnswer] = useState<AnswerResult | null>(null)
  const [selectedSourceIndex, setSelectedSourceIndex] = useState<number | null>(null)

  const selectedDocument = useMemo(
    () => documents.find((document) => document.id === selectedDocumentId) ?? null,
    [documents, selectedDocumentId],
  )

  const selectedSource = useMemo(() => {
    if (!answer?.sources?.length) return null
    if (selectedSourceIndex === null) return answer.sources[0]
    return answer.sources.find((source) => source.index === selectedSourceIndex) ?? answer.sources[0]
  }, [answer, selectedSourceIndex])

  const refreshDocuments = async () => {
    try {
      setLoadingDocuments(true)
      const data = await request<DocumentItem[]>('/documents')
      setDocuments(data)
      if (!selectedDocumentId && data[0]) {
        setSelectedDocumentId(data[0].id)
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to load documents.')
    } finally {
      setLoadingDocuments(false)
    }
  }

  useEffect(() => {
    void refreshDocuments()
  }, [])

  const handleUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      const uploaded = await request<DocumentItem>('/documents/upload', {
        method: 'POST',
        body: formData,
      })
      setSelectedDocumentId(uploaded.id)
      await refreshDocuments()
      setAnswer(null)
      setSelectedSourceIndex(null)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Upload failed.')
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  const handleSubmitQuestion = async (event: FormEvent) => {
    event.preventDefault()
    if (!selectedDocumentId) {
      setError('Select or upload a document before asking a question.')
      return
    }
    const trimmedQuestion = question.trim()
    if (!trimmedQuestion) {
      setError('Please enter a question.')
      return
    }

    setQuestionLoading(true)
    setError(null)

    try {
      const result = await request<AnswerResult>(`/documents/${selectedDocumentId}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: trimmedQuestion }),
      })
      setAnswer(result)
      setSelectedSourceIndex(result.sources[0]?.index ?? null)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to answer the question.')
      setAnswer(null)
    } finally {
      setQuestionLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI-powered document intelligence</p>
          <h1>DocuMind</h1>
        </div>
        <button type="button" className="secondary-button" onClick={() => void refreshDocuments()}>
          Refresh
        </button>
      </header>

      <main className="layout">
        <aside className="sidebar card">
          <div className="card-header">
            <h2>Documents</h2>
          </div>

          <label className="upload-box" aria-label="Upload a PDF or TXT document">
            <input type="file" accept=".pdf,.txt" onChange={handleUpload} disabled={uploading} />
            <span className="upload-label">{uploading ? 'Uploading…' : 'Upload PDF or TXT'}</span>
          </label>

          {error ? <p className="inline-error">{error}</p> : null}

          <div className="document-list">
            {loadingDocuments ? (
              <p className="muted">Loading documents…</p>
            ) : documents.length === 0 ? (
              <p className="muted">No documents uploaded yet.</p>
            ) : (
              documents.map((document) => (
                <button
                  key={document.id}
                  type="button"
                  className={`document-tile ${document.id === selectedDocumentId ? 'selected' : ''}`}
                  onClick={() => {
                    setSelectedDocumentId(document.id)
                    setAnswer(null)
                    setSelectedSourceIndex(null)
                  }}
                >
                  <div className="document-title-row">
                    <span className="file-name">{document.filename}</span>
                    <span className={`pill ${document.status}`}>{document.status}</span>
                  </div>
                  <div className="meta-row">
                    <span>{formatBytes(document.size_bytes)}</span>
                    <span>{formatDate(document.created_at)}</span>
                  </div>
                </button>
              ))
            )}
          </div>
        </aside>

        <section className="workspace card">
          {selectedDocument ? (
            <>
              <div className="document-header">
                <div>
                  <p className="eyebrow">Selected document</p>
                  <h2>{selectedDocument.filename}</h2>
                </div>
                <span className={`pill ${selectedDocument.status}`}>{selectedDocument.status}</span>
              </div>

              <form className="question-form" onSubmit={handleSubmitQuestion}>
                <label htmlFor="question" className="sr-only">
                  Ask a question
                </label>
                <textarea
                  id="question"
                  rows={3}
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Ask a question about the document…"
                  disabled={questionLoading}
                />
                <div className="action-row">
                  <button type="submit" className="primary-button" disabled={questionLoading || !selectedDocument}>
                    {questionLoading ? 'Processing…' : 'Ask DocuMind'}
                  </button>
                </div>
              </form>

              <div className="answer-panel">
                {answer ? (
                  <>
                    <div className="answer-header">
                      <h3>Answer</h3>
                      <span className="status-tag">{answer.status}</span>
                    </div>
                    <p className="answer-text">{answer.answer}</p>

                    {answer.sources?.length ? (
                      <div className="reference-list" aria-label="Source references">
                        {answer.sources.map((source) => (
                          <button
                            key={source.index}
                            type="button"
                            className={`source-button ${selectedSourceIndex === source.index ? 'active' : ''}`}
                            onClick={() => setSelectedSourceIndex(source.index)}
                          >
                            Source {source.index}
                            {source.page ? ` · Page ${source.page}` : ' · Page unavailable'}
                          </button>
                        ))}
                      </div>
                    ) : null}
                  </>
                ) : (
                  <p className="muted">Ask a question to get evidence-backed answers.</p>
                )}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <h2>No document selected</h2>
              <p>Upload a PDF or TXT file to begin.</p>
            </div>
          )}
        </section>

        <aside className="source-pane card">
          <div className="card-header">
            <h2>Source passages</h2>
          </div>
          {selectedSource ? (
            <>
              <p className="source-label">
                Source {selectedSource.index}
                {selectedSource.page ? ` · page ${selectedSource.page}` : ' · page unavailable'}
              </p>
              <p className="source-text">{selectedSource.text}</p>
            </>
          ) : (
            <p className="muted">Select a source reference to inspect the relevant passage.</p>
          )}
        </aside>
      </main>
    </div>
  )
}

export default App
