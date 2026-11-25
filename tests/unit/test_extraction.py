"""Acceptance tests for supported text extraction."""

from pathlib import Path

import pytest
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from engineering_assistant.services.extraction import extract_text


@pytest.mark.parametrize("suffix", [".txt", ".md", ".TXT", ".MD"])
def test_extracts_utf8_text(tmp_path: Path, suffix: str) -> None:
    path = tmp_path / f"guide{suffix}"
    path.write_text("UPV – software engineering", encoding="utf-8")
    assert extract_text(path) == "UPV – software engineering"


def test_extracts_pdf_text(tmp_path: Path) -> None:
    path = tmp_path / "guide.pdf"
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_reference = writer._add_object(font)
    font_resources = DictionaryObject({NameObject("/F1"): font_reference})
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): font_resources}
    )
    content = DecodedStreamObject()
    content.set_data(b"BT /F1 12 Tf 40 240 Td (PDF extraction works) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(content)
    with path.open("wb") as pdf_file:
        writer.write(pdf_file)

    assert extract_text(path) == "PDF extraction works"


def test_rejects_unsupported_extension(tmp_path: Path) -> None:
    path = tmp_path / "diagram.png"
    path.write_bytes(b"not a document")
    with pytest.raises(ValueError):
        extract_text(path)
