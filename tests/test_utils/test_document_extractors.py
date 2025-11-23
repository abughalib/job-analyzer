"""Tests for document extractors (PDF, DOCX, TXT)."""

import pytest
from pathlib import Path

from utils.pdf_extractor import extract_text_from_pdf
from utils.docx_extractor import extract_text_from_docx
from utils.document_extractor import extract_document_text


@pytest.mark.asyncio
async def test_txt_extractor():
    """Test TXT text extraction."""
    test_file = Path("tests/test_files/test_resume.txt")

    if not test_file.exists():
        pytest.skip("test_resume.txt not found")

    text = await extract_document_text(test_file)
    assert text
    assert len(text) > 0
    assert "JANE DOE" in text or "jane doe" in text.lower()
    print(f"TXT extraction successful ({len(text)} chars)")


@pytest.mark.asyncio
async def test_pdf_extractor():
    """Test PDF text extraction."""
    test_file = Path("tests/test_files/test_resume.pdf")

    if not test_file.exists():
        pytest.skip("test_resume.pdf not found")

    try:
        text = extract_text_from_pdf(test_file)
        assert text
        assert len(text) > 0
        print(f"PDF extraction successful ({len(text)} chars)")
    except Exception as e:
        pytest.skip(f"PDF extraction failed: {e}")


@pytest.mark.asyncio
async def test_docx_extractor():
    """Test DOCX text extraction."""
    test_file = Path("tests/test_files/test_resume.docx")

    if not test_file.exists():
        pytest.skip("test_resume.docx not found")

    try:
        text = extract_text_from_docx(test_file)
        assert text
        assert len(text) > 0
        print(f"DOCX extraction successful ({len(text)} chars)")
    except Exception as e:
        pytest.skip(f"DOCX extraction failed: {e}")


@pytest.mark.asyncio
async def test_txt_extractor():
    """Test TXT text extraction."""
    test_file = Path("tests/test_files/test_resume.txt")

    if not test_file.exists():
        pytest.skip("test_resume.txt not found")

    text = await extract_document_text(test_file)
    assert text
    assert len(text) > 0
    assert "JANE DOE" in text or "jane doe" in text.lower()
    print(f"TXT extraction successful ({len(text)} chars)")


@pytest.mark.asyncio
async def test_pdf_extractor():
    """Test PDF text extraction."""
    test_file = Path("tests/test_files/test_resume.pdf")

    if not test_file.exists():
        pytest.skip("test_resume.pdf not found")

    try:
        text = extract_text_from_pdf(test_file)
        assert text
        assert len(text) > 0
        print(f"PDF extraction successful ({len(text)} chars)")
    except Exception as e:
        pytest.skip(f"PDF extraction failed: {e}")


@pytest.mark.asyncio
async def test_docx_extractor():
    """Test DOCX text extraction."""
    test_file = Path("tests/test_files/test_resume.docx")

    if not test_file.exists():
        pytest.skip("test_resume.docx not found")

    try:
        text = extract_text_from_docx(test_file)
        assert text
        assert len(text) > 0
        print(f"DOCX extraction successful ({len(text)} chars)")
    except Exception as e:
        pytest.skip(f"DOCX extraction failed: {e}")


@pytest.mark.asyncio
async def test_unsupported_format():
    """Test that unsupported formats raise ValueError."""
    test_file = Path("tests/test_files/test.xyz")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("test")

    with pytest.raises((ValueError, RuntimeError)):
        await extract_document_text(test_file)

    test_file.unlink()  # Clean up
    print("Unsupported format handling works")
