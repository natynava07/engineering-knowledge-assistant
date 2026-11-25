"""Acceptance tests for SQLite document persistence."""

from pathlib import Path

import pytest

from engineering_assistant.repositories.documents import (
    delete_document,
    get_document,
    initialize_database,
    list_documents,
    save_document,
    search_chunks,
)
from engineering_assistant.services.catalog import DocumentInfo


def sample_info() -> DocumentInfo:
    return DocumentInfo(
        name="guide.md",
        relative_path="guides/guide.md",
        extension=".md",
        size_bytes=20,
    )


def test_insert_list_get_and_delete(tmp_path: Path) -> None:
    db = tmp_path / "catalogue.sqlite3"
    initialize_database(db)
    document_id = save_document(db, sample_info(), "a" * 64, ["alpha", "beta"])

    rows = list_documents(db)
    assert len(rows) == 1
    assert rows[0]["relative_path"] == "guides/guide.md"
    assert get_document(db, document_id) is not None
    assert delete_document(db, document_id) is True
    assert get_document(db, document_id) is None
    assert delete_document(db, document_id) is False


def test_upsert_same_path_replaces_chunks(tmp_path: Path) -> None:
    db = tmp_path / "catalogue.sqlite3"
    initialize_database(db)
    first = save_document(db, sample_info(), "a" * 64, ["old text"])
    second = save_document(db, sample_info(), "b" * 64, ["new text"])

    assert first == second
    assert len(list_documents(db)) == 1
    assert search_chunks(db, "new")[0]["text"] == "new text"
    assert search_chunks(db, "old") == []


def test_search_rejects_invalid_arguments(tmp_path: Path) -> None:
    db = tmp_path / "catalogue.sqlite3"
    initialize_database(db)
    with pytest.raises(ValueError):
        search_chunks(db, "")
    with pytest.raises(ValueError):
        search_chunks(db, "alpha", limit=0)
