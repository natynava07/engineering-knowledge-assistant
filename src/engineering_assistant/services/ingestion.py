"""Coordinate document discovery, extraction, chunking and persistence."""

from pathlib import Path


def ingest_directory(
    documents_root: Path,
    database_path: Path,
    max_chars: int = 1_000,
    overlap: int = 150,
) -> dict[str, int]:
    """Ingest supported files below documents_root.

    Compose the catalogue, extraction, chunking and repository layers. Do not
    duplicate their responsibilities here. Calculate SHA-256 for each file.
    Re-ingesting the same relative path must update, not duplicate, its record.

    Return discovered, indexed and skipped counts. Choose and document how a
    single-file failure is handled.

    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement ingest_directory")
