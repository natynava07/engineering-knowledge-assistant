"""Additional unit tests for extraction, chunking and SQLite edge cases."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from engineering_assistant.repositories.documents import (
    delete_document,
    initialize_database,
    list_documents,
    save_document,
    search_chunks,
)
from engineering_assistant.services.catalog import DocumentInfo
from engineering_assistant.services.chunking import chunk_text
from engineering_assistant.services.extraction import extract_text


def make_info(relative_path: str) -> DocumentInfo:
    return DocumentInfo(
        name=Path(relative_path).name,
        relative_path=relative_path,
        extension=Path(relative_path).suffix,
        size_bytes=10,
    )


def count_chunks(db: Path) -> int:
    with closing(sqlite3.connect(db)) as connection:
        row = connection.execute("SELECT COUNT(*) FROM chunks").fetchone()
    return int(row[0])


def test_invalid_utf8_is_not_silently_ignored(tmp_path: Path) -> None:
    path = tmp_path / "broken.txt"
    path.write_bytes(b"\xff\xfe not utf-8 \xff")
    with pytest.raises(UnicodeDecodeError):
        extract_text(path)


def test_long_text_respects_limit_and_overlap() -> None:
    text = "".join(chr(ord("a") + i % 26) for i in range(2_500))
    chunks = chunk_text(text, max_chars=1_000, overlap=150)

    assert len(chunks) == 3
    assert all(len(chunk) <= 1_000 for chunk in chunks)
    for previous, current in zip(chunks, chunks[1:], strict=False):
        assert previous[-150:] == current[:150]


def test_short_text_is_a_single_chunk() -> None:
    assert chunk_text("short text", max_chars=100, overlap=10) == ["short text"]


def test_listing_is_sorted_by_relative_path(tmp_path: Path) -> None:
    db = tmp_path / "catalogue.sqlite3"
    initialize_database(db)
    for relative_path in ["z.txt", "a/b.md", "m.pdf"]:
        save_document(db, make_info(relative_path), "c" * 64, ["text"])

    paths = [row["relative_path"] for row in list_documents(db)]

    assert paths == ["a/b.md", "m.pdf", "z.txt"]


def test_deleting_a_document_cascades_to_its_chunks(tmp_path: Path) -> None:
    db = tmp_path / "catalogue.sqlite3"
    initialize_database(db)
    keep = save_document(db, make_info("keep.txt"), "a" * 64, ["one"])
    remove = save_document(db, make_info("remove.txt"), "b" * 64, ["two", "three"])
    assert count_chunks(db) == 3

    assert delete_document(db, remove) is True

    assert count_chunks(db) == 1
    assert [row["id"] for row in list_documents(db)] == [keep]


def test_search_is_case_insensitive_and_bounded(tmp_path: Path) -> None:
    db = tmp_path / "catalogue.sqlite3"
    initialize_database(db)
    save_document(
        db, make_info("guide.md"), "a" * 64, ["Pump SAFETY", "safety valve", "other"]
    )

    results = search_chunks(db, "Safety")
    assert [row["chunk_index"] for row in results] == [0, 1]
    assert results[0]["document_name"] == "guide.md"
    assert len(search_chunks(db, "safety", limit=1)) == 1


def test_search_treats_wildcards_literally(tmp_path: Path) -> None:
    db = tmp_path / "catalogue.sqlite3"
    initialize_database(db)
    save_document(db, make_info("rates.txt"), "a" * 64, ["100% done", "plain"])

    assert [row["text"] for row in search_chunks(db, "%")] == ["100% done"]
    assert search_chunks(db, "_") == []
