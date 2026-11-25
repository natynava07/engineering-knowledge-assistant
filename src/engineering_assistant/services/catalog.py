"""Discover and describe documents for the course project.

These functions are the Class 1 starter tasks. They intentionally remain
unfinished in the public Class 2 snapshot. Read the unit tests before coding.
"""

from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


@dataclass(frozen=True, slots=True)
class DocumentInfo:
    """Metadata recorded for one supported document."""

    name: str
    relative_path: str
    extension: str
    size_bytes: int


def is_supported_document(path: Path) -> bool:
    """Return True when path is a regular file with a supported extension.

    Extension matching must be case-insensitive. Directories are not documents.
    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement is_supported_document")


def discover_documents(root: Path) -> list[Path]:
    """Recursively find supported documents below root.

    Return paths rooted at root, sorted by their relative POSIX path.
    Return an empty list when root does not exist. Raise NotADirectoryError when
    root exists but is not a directory.
    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement discover_documents")


def describe_document(path: Path, root: Path) -> DocumentInfo:
    """Create metadata for path, using a path relative to root.

    Store the original filename, a POSIX relative path, a lower-case extension,
    and the file size in bytes. Raise ValueError for unsupported files or paths
    outside root.
    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement describe_document")


def build_manifest(root: Path) -> list[DocumentInfo]:
    """Return metadata for every supported document below root.

    Use discover_documents and describe_document rather than duplicating logic.
    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement build_manifest")
