"""Additional API and ingestion tests covering a full workflow and errors."""

from pathlib import Path

from fastapi.testclient import TestClient

from engineering_assistant.main import create_app
from engineering_assistant.repositories.documents import list_documents
from engineering_assistant.services.ingestion import ingest_directory


def make_documents(tmp_path: Path) -> Path:
    documents = tmp_path / "documents"
    (documents / "manuals").mkdir(parents=True)
    (documents / "manuals" / "pump.md").write_text(
        "# Pump\nCheck the pressure valve weekly.", encoding="utf-8"
    )
    (documents / "notes.txt").write_text("Coffee machine notes.", encoding="utf-8")
    return documents


def make_client(tmp_path: Path) -> TestClient:
    app = create_app(
        database_path=tmp_path / "catalogue.sqlite3",
        documents_root=make_documents(tmp_path),
    )
    return TestClient(app, raise_server_exceptions=False)


def test_ingest_list_get_search_and_delete(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    ingest = client.post("/documents/ingest")
    assert ingest.status_code == 200
    assert ingest.json() == {"discovered": 2, "indexed": 2, "skipped": 0}

    documents = client.get("/documents").json()
    assert [doc["relative_path"] for doc in documents] == [
        "manuals/pump.md",
        "notes.txt",
    ]
    pump_id = documents[0]["id"]
    assert len(documents[0]["sha256"]) == 64

    detail = client.get(f"/documents/{pump_id}")
    assert detail.status_code == 200
    assert detail.json()["name"] == "pump.md"

    search = client.get("/search", params={"q": "VALVE"})
    assert search.status_code == 200
    assert [hit["document_id"] for hit in search.json()] == [pump_id]

    assert client.delete(f"/documents/{pump_id}").status_code == 204
    assert client.get(f"/documents/{pump_id}").status_code == 404
    assert client.get("/search", params={"q": "valve"}).json() == []


def test_delete_missing_document_returns_404(tmp_path: Path) -> None:
    assert make_client(tmp_path).delete("/documents/999").status_code == 404


def test_search_validation_errors(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    assert client.get("/search").status_code == 422
    assert client.get("/search", params={"q": "   "}).status_code == 422
    assert client.get("/search", params={"q": "a", "limit": 0}).status_code == 422
    assert client.get("/search", params={"q": "a", "limit": 101}).status_code == 422
    assert client.get("/documents/abc").status_code == 422


def test_reingesting_does_not_duplicate_documents(tmp_path: Path) -> None:
    documents = make_documents(tmp_path)
    database = tmp_path / "catalogue.sqlite3"

    ingest_directory(documents, database)
    first_ids = [row["id"] for row in list_documents(database)]
    ingest_directory(documents, database)

    assert [row["id"] for row in list_documents(database)] == first_ids


def test_unreadable_file_is_skipped_and_others_indexed(tmp_path: Path) -> None:
    documents = make_documents(tmp_path)
    (documents / "broken.txt").write_bytes(b"\xff\xfe\xff")
    (documents / "fake.pdf").write_bytes(b"this is not a real pdf")
    database = tmp_path / "catalogue.sqlite3"

    summary = ingest_directory(documents, database)

    assert summary == {"discovered": 4, "indexed": 2, "skipped": 2}
    assert len(list_documents(database)) == 2
