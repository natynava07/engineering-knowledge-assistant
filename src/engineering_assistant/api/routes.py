"""HTTP route declarations for the Engineering Knowledge Assistant."""

from fastapi import APIRouter, Query, status

from engineering_assistant.api.schemas import (
    DocumentResponse,
    IngestResponse,
    SearchResultResponse,
)

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Return a lightweight process health check."""
    return {"status": "ok"}


@router.post(
    "/documents/ingest", response_model=IngestResponse, status_code=status.HTTP_200_OK
)
def ingest_documents() -> IngestResponse:
    """Trigger ingestion of the configured local documents directory.

    TODO: call the ingestion service and return its summary.
    """
    raise NotImplementedError("TODO: implement POST /documents/ingest")


@router.get("/documents", response_model=list[DocumentResponse])
def get_documents() -> list[DocumentResponse]:
    """List indexed document metadata.

    TODO: call the documents repository and map rows to response models.
    """
    raise NotImplementedError("TODO: implement GET /documents")


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document_by_id(document_id: int) -> DocumentResponse:
    """Return one document or HTTP 404.

    TODO: retrieve the document and translate a missing row into HTTP 404.
    """
    raise NotImplementedError("TODO: implement GET /documents/{document_id}")


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(document_id: int) -> None:
    """Delete a document and its chunks or return HTTP 404.

    TODO: call the repository and return HTTP 204 or HTTP 404.
    """
    raise NotImplementedError("TODO: implement DELETE /documents/{document_id}")


@router.get("/search", response_model=list[SearchResultResponse])
def search(
    q: str = Query(min_length=1), limit: int = Query(default=10, ge=1, le=100)
) -> list[SearchResultResponse]:
    """Search indexed chunks using literal case-insensitive keywords.

    TODO: call the repository search function and map rows to response models.
    """
    raise NotImplementedError("TODO: implement GET /search")
