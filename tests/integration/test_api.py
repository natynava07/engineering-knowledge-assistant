"""Integration tests for the FastAPI HTTP contract."""

from pathlib import Path

from fastapi.testclient import TestClient

from engineering_assistant.main import create_app


def make_client(tmp_path: Path) -> TestClient:
    app = create_app(
        database_path=tmp_path / "catalogue.sqlite3",
        documents_root=tmp_path / "documents",
    )
    return TestClient(app, raise_server_exceptions=False)


def test_health_endpoint(tmp_path: Path) -> None:
    response = make_client(tmp_path).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_documents_contract(tmp_path: Path) -> None:
    response = make_client(tmp_path).get("/documents")
    assert response.status_code == 200
    assert response.json() == []


def test_missing_document_returns_404(tmp_path: Path) -> None:
    response = make_client(tmp_path).get("/documents/999")
    assert response.status_code == 404


def test_search_requires_a_query(tmp_path: Path) -> None:
    response = make_client(tmp_path).get("/search?q=")
    assert response.status_code == 422
