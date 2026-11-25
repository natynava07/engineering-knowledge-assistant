"""Extract text from supported PDF, TXT and Markdown documents."""

from pathlib import Path


def extract_text(path: Path) -> str:
    """Extract text from a supported file.

    Requirements:
    - Match supported extensions case-insensitively.
    - Decode TXT and Markdown as UTF-8.
    - Use pypdf to extract PDF pages in order and join non-empty page text.
    - Raise ValueError for unsupported extensions.
    - Do not silently swallow decoding or parsing errors.

    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement extract_text")
