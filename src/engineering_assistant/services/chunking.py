"""Split extracted document text into deterministic overlapping chunks."""


def chunk_text(text: str, max_chars: int = 1_000, overlap: int = 150) -> list[str]:
    """Split normalized text into ordered character windows.

    Requirements:
    - Return [] for empty or whitespace-only text.
    - Collapse runs of whitespace to one space before chunking.
    - No chunk may exceed max_chars.
    - Consecutive chunks should overlap by the requested amount where possible.
    - Raise ValueError for max_chars <= 0, overlap < 0, or overlap >= max_chars.

    TODO: implement this function.
    """
    raise NotImplementedError("TODO: implement chunk_text")
