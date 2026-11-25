"""Split extracted document text into deterministic overlapping chunks."""


def chunk_text(text: str, max_chars: int = 1_000, overlap: int = 150) -> list[str]:
    """Split normalized text into ordered character windows.

    Runs of whitespace are collapsed to one space first. Each chunk has at most
    max_chars characters and starts overlap characters before the end of the
    previous one. Raise ValueError for max_chars <= 0, overlap < 0, or
    overlap >= max_chars.
    """
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than zero")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars")

    normalized = " ".join(text.split())
    if not normalized:
        return []

    step = max_chars - overlap
    chunks: list[str] = []
    start = 0
    while True:
        end = start + max_chars
        chunks.append(normalized[start:end])
        if end >= len(normalized):
            break
        start += step
    return chunks
