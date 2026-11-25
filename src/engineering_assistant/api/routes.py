"""HTTP route declarations for the Engineering Knowledge Assistant."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from engineering_assistant.api.schemas import (
    DocumentResponse,
    IngestResponse,
    SearchResultResponse,
)
from engineering_assistant.repositories.documents import (
    delete_document,
    get_document,
    initialize_database,
    list_documents,
    search_chunks,
)
from engineering_assistant.services.ingestion import ingest_directory

router = APIRouter()


def get_database_path(request: Request) -> Path:
    """Return the configured database path, creating the schema if needed."""
    database_path: Path = request.app.state.database_path
    initialize_database(database_path)
    return database_path


def get_documents_root(request: Request) -> Path:
    """Return the configured documents directory."""
    documents_root: Path = request.app.state.documents_root
    return documents_root


DatabasePath = Annotated[Path, Depends(get_database_path)]
DocumentsRoot = Annotated[Path, Depends(get_documents_root)]


@router.get("/health")
def health() -> dict[str, str]:
    """Return a lightweight process health check."""
    return {"status": "ok"}


@router.post(
    "/documents/ingest", response_model=IngestResponse, status_code=status.HTTP_200_OK
)
def ingest_documents(
    database_path: DatabasePath, documents_root: DocumentsRoot
) -> IngestResponse:
    """Trigger ingestion of the configured local documents directory."""
    try:
        summary = ingest_directory(documents_root, database_path)
    except NotADirectoryError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        ) from error
    return IngestResponse(**summary)


@router.get("/documents", response_model=list[DocumentResponse])
def get_documents(database_path: DatabasePath) -> list[DocumentResponse]:
    """List indexed document metadata."""
    return [DocumentResponse(**row) for row in list_documents(database_path)]


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document_by_id(
    document_id: int, database_path: DatabasePath
) -> DocumentResponse:
    """Return one document or HTTP 404."""
    row = get_document(database_path, document_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return DocumentResponse(**row)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(document_id: int, database_path: DatabasePath) -> None:
    """Delete a document and its chunks or return HTTP 404."""
    if not delete_document(database_path, document_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )


@router.get("/search", response_model=list[SearchResultResponse])
def search(
    database_path: DatabasePath,
    q: str = Query(min_length=1),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[SearchResultResponse]:
    """Search indexed chunks using literal case-insensitive keywords."""
    try:
        rows = search_chunks(database_path, q, limit)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    return [SearchResultResponse(**row) for row in rows]
