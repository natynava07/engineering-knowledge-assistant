"""Pydantic response models exposed by the HTTP API."""

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    name: str
    relative_path: str
    extension: str
    size_bytes: int
    sha256: str
    created_at: str


class IngestResponse(BaseModel):
    discovered: int
    indexed: int
    skipped: int


class SearchResultResponse(BaseModel):
    document_id: int
    document_name: str
    relative_path: str
    chunk_index: int
    text: str
