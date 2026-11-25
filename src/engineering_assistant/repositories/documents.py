"""SQLite access for document metadata and extracted text chunks."""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from engineering_assistant.services.catalog import DocumentInfo


def initialize_database(database_path: Path) -> None:
    """Create documents/chunks tables, constraints, foreign keys and indexes.

    Required document fields: id, name, relative_path (unique), extension,
    size_bytes, sha256 and created_at. Required chunk fields: id, document_id,
    chunk_index and text. Deleting a document must cascade to its chunks.

    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement initialize_database")


def save_document(
    database_path: Path, info: DocumentInfo, sha256: str, chunks: Sequence[str]
) -> int:
    """Insert/update a document and replace its chunks; return its database id.

    Use a unique relative_path so repeated ingestion does not create duplicates.
    Use parameterized SQL for every value.

    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement save_document")


def list_documents(database_path: Path) -> list[dict[str, Any]]:
    """Return document metadata in deterministic relative-path order.

    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement list_documents")


def get_document(database_path: Path, document_id: int) -> dict[str, Any] | None:
    """Return one document's metadata, or None when it does not exist.

    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement get_document")


def delete_document(database_path: Path, document_id: int) -> bool:
    """Delete one document and its chunks; return whether it existed.

    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement delete_document")


def search_chunks(
    database_path: Path, query: str, limit: int = 10
) -> list[dict[str, Any]]:
    """Return case-insensitive keyword matches, with a bounded result count.

    Reject an empty query and non-positive limits. Use parameterized SQL.

    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement search_chunks")
