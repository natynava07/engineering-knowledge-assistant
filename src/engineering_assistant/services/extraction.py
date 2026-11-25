"""Extract text from supported PDF, TXT and Markdown documents."""

from pathlib import Path

from pypdf import PdfReader

TEXT_EXTENSIONS = {".txt", ".md"}
PDF_EXTENSION = ".pdf"


def extract_text(path: Path) -> str:
    """Extract text from a supported file.

    TXT and Markdown files are decoded as UTF-8. PDF pages are read with pypdf
    in order and the non-empty page texts are joined with a blank line.
    Unsupported extensions raise ValueError. Decoding and PDF parsing errors are
    not caught here, so the caller decides how to handle them.
    """
    extension = path.suffix.lower()
    if extension in TEXT_EXTENSIONS:
        return path.read_text(encoding="utf-8")
    if extension == PDF_EXTENSION:
        reader = PdfReader(path)
        pages = [page.extract_text() for page in reader.pages]
        return "\n\n".join(text.strip() for text in pages if text and text.strip())
    raise ValueError(f"Unsupported document type: {path.suffix or '(none)'}")
