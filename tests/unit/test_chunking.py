"""Acceptance tests for deterministic text chunking."""

import pytest

from engineering_assistant.services.chunking import chunk_text


def test_empty_and_whitespace_input_returns_no_chunks() -> None:
    assert chunk_text("") == []
    assert chunk_text("  \n  ") == []


def test_chunks_are_ordered_and_overlap() -> None:
    assert chunk_text("abcdefghij", max_chars=4, overlap=1) == ["abcd", "defg", "ghij"]


def test_whitespace_is_normalized() -> None:
    assert chunk_text("one  two\nthree", max_chars=20, overlap=0) == ["one two three"]


@pytest.mark.parametrize("max_chars, overlap", [(0, 0), (10, -1), (10, 10)])
def test_invalid_windows_raise(max_chars: int, overlap: int) -> None:
    with pytest.raises(ValueError):
        chunk_text("some text", max_chars=max_chars, overlap=overlap)
