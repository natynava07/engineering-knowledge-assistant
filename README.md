# Engineering Knowledge Assistant

A small, testable document service. It indexes a local collection of PDF, TXT and Markdown documents into SQLite,
exposes the catalogue through a REST API, and offers a simple keyword search over the extracted text.

This is the Class 2 milestone of the UPV AI-assisted software development course. It builds on the Class 1 document
catalogue. It is deliberately **not** an AI/RAG system: there is no LLM, no embeddings and no vector database.

## Requirements and setup

- Python >= 3.12
- Git, GNU Make and [uv](https://docs.astral.sh/uv/)
- Linux, macOS, Windows with WSL2, or GitHub Codespaces

```bash
make install-test        # create .venv and install runtime, dev and test dependencies
uv run pre-commit install
```

Dependencies are pinned in `uv.lock` (FastAPI, Uvicorn, Pydantic, pypdf; pytest, httpx, ruff and mypy for development).

## Architecture

```text
src/engineering_assistant/
├── api/
│   ├── routes.py         # HTTP routes: validation, status codes, no SQL
│   └── schemas.py        # Pydantic response models
├── services/
│   ├── catalog.py        # Class 1: discover and describe supported files
│   ├── extraction.py     # TXT/MD (UTF-8) and PDF (pypdf) text extraction
│   ├── chunking.py       # deterministic overlapping character chunks
│   └── ingestion.py      # composes catalog -> extract -> sha256 -> chunk -> save
├── repositories/
│   └── documents.py      # SQLite schema and parameterized SQL queries
└── main.py               # FastAPI application factory
```

Each layer only talks to the layer below it. Route handlers are thin: they read the configured paths, call a service or
repository function and translate the result into an HTTP response (for example, `None` becomes 404).

### Database schema

- `documents`: `id` (primary key), `name`, `relative_path` (**unique**), `extension`, `size_bytes`, `sha256`,
  `created_at` (UTC ISO timestamp of the last indexing).
- `chunks`: `id` (primary key), `document_id` (foreign key to `documents.id`, `ON DELETE CASCADE`), `chunk_index`
  (zero-based), `text`, with `UNIQUE (document_id, chunk_index)` and an index on `document_id`.

Every connection runs `PRAGMA foreign_keys = ON`, and every value is passed as a SQL parameter.

### Ingestion and error policy

`ingest_directory` builds the Class 1 manifest and, for each file, extracts the text, calculates its SHA-256, splits it
into chunks and saves it. Saving a document is an upsert on `relative_path`: re-ingesting the same file updates the row
and replaces its chunks instead of creating a duplicate.

If one file cannot be read, decoded as UTF-8 or parsed as a PDF, it is logged, counted as `skipped`, and ingestion
continues with the next file. Each document is saved in its own transaction, so a failure never leaves a half-written
document and never changes documents that were already indexed.

## Commands

```bash
make lint      # ruff (lint + format check) and mypy --strict
make format    # apply ruff formatting and import sorting
make test      # pytest with coverage (unit + integration)
uv run pre-commit run --all-files
```

### Run the API

Put some documents in `data/documents/` (this folder is gitignored), then:

```bash
uv run uvicorn engineering_assistant.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the Swagger UI. The database is created at `data/catalogue.sqlite3`.

| Method | Endpoint                   | Behaviour                                         |
|--------|----------------------------|---------------------------------------------------|
| GET    | `/health`                  | `{"status": "ok"}`                                |
| POST   | `/documents/ingest`        | Index `data/documents/`, return counts            |
| GET    | `/documents`               | List documents ordered by relative path           |
| GET    | `/documents/{document_id}` | One document, or 404                              |
| DELETE | `/documents/{document_id}` | Delete a document and its chunks (204), or 404    |
| GET    | `/search?q=...&limit=10`   | Case-insensitive keyword search (422 if invalid)  |

## Tests

- `tests/unit/`: catalogue (Class 1, unchanged), extraction, chunking, repository and extra edge cases
  (`test_edge_cases.py`: invalid UTF-8, long text, ordering, cascade delete, bounded and literal search).
- `tests/integration/`: API contract and ingestion, plus `test_api_workflow.py` (full ingest/list/get/search/delete
  flow, validation errors, 404 on delete, re-ingestion without duplicates, skipping broken files).

## Known limitations

- **No OCR**: scanned PDFs (images of text) produce little or no text and are indexed with few or no chunks.
- Keyword search is a literal substring match (`LIKE`): no ranking, stemming, synonyms or meaning. "pumps" does not
  match "pump" and `lower()` only folds ASCII letters, so accented capitals may not match.
- Chunks are cut by character count, so a chunk can start or end in the middle of a word.
- Ingestion is synchronous and re-processes every file, even if its SHA-256 has not changed.
- Files deleted from disk are not removed from the database automatically.
- No authentication; the API is meant to run locally.
