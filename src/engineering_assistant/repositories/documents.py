"""SQLite access for document metadata and extracted text chunks."""

import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from engineering_assistant.services.catalog import DocumentInfo

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    relative_path TEXT NOT NULL UNIQUE,
    extension TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL
        REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    text TEXT NOT NULL,
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
"""

DOCUMENT_COLUMNS = "id, name, relative_path, extension, size_bytes, sha256, created_at"


@contextmanager
def connect(database_path: Path) -> Iterator[sqlite3.Connection]:
    """Open a connection with foreign keys on; commit or roll back, then close."""
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(database_path: Path) -> None:
    """Create documents/chunks tables, constraints, foreign keys and indexes."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(database_path) as connection:
        connection.executescript(SCHEMA)


def save_document(
    database_path: Path, info: DocumentInfo, sha256: str, chunks: Sequence[str]
) -> int:
    """Insert/update a document and replace its chunks; return its database id.

    Everything happens in one transaction, so a failure leaves the previous
    version of the document untouched.
    """
    created_at = datetime.now(UTC).isoformat()
    with connect(database_path) as connection:
        row = connection.execute(
            """
            INSERT INTO documents
                (name, relative_path, extension, size_bytes, sha256, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(relative_path) DO UPDATE SET
                name = excluded.name,
                extension = excluded.extension,
                size_bytes = excluded.size_bytes,
                sha256 = excluded.sha256,
                created_at = excluded.created_at
            RETURNING id
            """,
            (
                info.name,
                info.relative_path,
                info.extension,
                info.size_bytes,
                sha256,
                created_at,
            ),
        ).fetchone()
        document_id = int(row["id"])
        connection.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
        connection.executemany(
            "INSERT INTO chunks (document_id, chunk_index, text) VALUES (?, ?, ?)",
            [(document_id, index, text) for index, text in enumerate(chunks)],
        )
    return document_id


def list_documents(database_path: Path) -> list[dict[str, Any]]:
    """Return document metadata in deterministic relative-path order."""
    with connect(database_path) as connection:
        rows = connection.execute(
            f"SELECT {DOCUMENT_COLUMNS} FROM documents ORDER BY relative_path, id"
        ).fetchall()
    return [dict(row) for row in rows]


def get_document(database_path: Path, document_id: int) -> dict[str, Any] | None:
    """Return one document's metadata, or None when it does not exist."""
    with connect(database_path) as connection:
        row = connection.execute(
            f"SELECT {DOCUMENT_COLUMNS} FROM documents WHERE id = ?", (document_id,)
        ).fetchone()
    return dict(row) if row is not None else None


def delete_document(database_path: Path, document_id: int) -> bool:
    """Delete one document and its chunks; return whether it existed."""
    with connect(database_path) as connection:
        cursor = connection.execute(
            "DELETE FROM documents WHERE id = ?", (document_id,)
        )
    return cursor.rowcount > 0


def _escape_like(value: str) -> str:
    """Escape LIKE wildcards so the query is matched literally."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_chunks(
    database_path: Path, query: str, limit: int = 10
) -> list[dict[str, Any]]:
    """Return case-insensitive keyword matches, with a bounded result count.

    Reject an empty query and non-positive limits. Use parameterized SQL.
    """
    keyword = query.strip()
    if not keyword:
        raise ValueError("query must not be empty")
    if limit <= 0:
        raise ValueError("limit must be greater than zero")
    pattern = f"%{_escape_like(keyword.lower())}%"
    with connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT
                chunks.document_id AS document_id,
                documents.name AS document_name,
                documents.relative_path AS relative_path,
                chunks.chunk_index AS chunk_index,
                chunks.text AS text
            FROM chunks
            JOIN documents ON documents.id = chunks.document_id
            WHERE lower(chunks.text) LIKE ? ESCAPE '\\'
            ORDER BY documents.relative_path, chunks.chunk_index
            LIMIT ?
            """,
            (pattern, limit),
        ).fetchall()
    return [dict(row) for row in rows]
