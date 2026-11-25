"""Integration tests for the ingestion workflow."""

from pathlib import Path

from engineering_assistant.repositories.documents import list_documents
from engineering_assistant.services.ingestion import ingest_directory


def test_ingestion_indexes_a_text_file(tmp_path: Path) -> None:
    documents = tmp_path / "documents"
    documents.mkdir()
    (documents / "guide.txt").write_text(
        "A test document for the knowledge assistant.", encoding="utf-8"
    )
    database = tmp_path / "catalogue.sqlite3"

    summary = ingest_directory(documents, database)

    assert summary["discovered"] == 1
    assert summary["indexed"] == 1
    assert summary["skipped"] == 0
    assert len(list_documents(database)) == 1
