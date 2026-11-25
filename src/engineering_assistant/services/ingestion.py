"""Coordinate document discovery, extraction, chunking and persistence."""

import hashlib
import logging
from pathlib import Path

from pypdf.errors import PdfReadError

from engineering_assistant.repositories.documents import (
    initialize_database,
    save_document,
)
from engineering_assistant.services.catalog import build_manifest
from engineering_assistant.services.chunking import chunk_text
from engineering_assistant.services.extraction import extract_text

logger = logging.getLogger(__name__)


def file_sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of a file, read in blocks."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(65_536), b""):
            digest.update(block)
    return digest.hexdigest()


def ingest_directory(
    documents_root: Path,
    database_path: Path,
    max_chars: int = 1_000,
    overlap: int = 150,
) -> dict[str, int]:
    """Ingest supported files below documents_root.

    Error policy: a file that cannot be read, decoded or parsed is logged and
    counted as skipped; the other files are still indexed. Each document is
    saved in its own transaction, so a failure never leaves half a document in
    the database and never touches documents that were already stored.
    """
    initialize_database(database_path)
    manifest = build_manifest(documents_root)
    indexed = 0
    skipped = 0
    for info in manifest:
        path = documents_root / info.relative_path
        try:
            text = extract_text(path)
            sha256 = file_sha256(path)
        except (OSError, UnicodeDecodeError, PdfReadError, ValueError) as error:
            logger.warning("Skipping %s: %s", info.relative_path, error)
            skipped += 1
            continue
        chunks = chunk_text(text, max_chars=max_chars, overlap=overlap)
        save_document(database_path, info, sha256, chunks)
        indexed += 1
    return {"discovered": len(manifest), "indexed": indexed, "skipped": skipped}
