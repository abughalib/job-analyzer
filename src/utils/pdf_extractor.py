#!/usr/bin/env python3
"""
PDF Text Extractor
Extracts text (and link annotations) from a PDF file and saves it as a .txt file.
"""

import logging
from pathlib import Path
from typing import List, Optional

from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extract all text content (and links) from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Concatenated text extracted from all pages.
    """
    pdf_path = Path(pdf_path)
    reader = PdfReader(str(pdf_path))
    text_chunks: List[str] = []

    for i, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        annotations = page.get("/Annots")

        # Extract link annotations (if any)
        if annotations:
            for annot in annotations:
                try:
                    annot_obj = annot.get_object()
                    action = annot_obj.get("/A")
                    if action:
                        uri = action.get("/URI")
                        if uri:
                            page_text += f"\n[Link: {uri}]"
                except Exception as e:
                    logger.debug(f"Warning: Failed to read annotation on page {i}: {e}")

        if page_text.strip():
            text_chunks.append(page_text)
        else:
            logger.debug(f"No text found on page {i}")

    return "\n\n".join(text_chunks).strip()


def save_extracted_text(
    pdf_path: str | Path, output_dir: Optional[str | Path] = None
) -> Path:
    """
    Extract text from a PDF and save it as a .txt file.

    Args:
        pdf_path: Path to the source PDF.
        output_dir: Output directory for the text file. Defaults to the same directory as the PDF.

    Returns:
        Path to the created text file.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    output_dir = Path(output_dir) if output_dir else pdf_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    txt_path = output_dir / f"{pdf_path.stem}.txt"

    logger.info(f"Extracting text from: {pdf_path}")
    text_content = extract_text_from_pdf(pdf_path)

    if not text_content:
        logger.warning(f"No extractable text found in: {pdf_path.name}")
        text_content = "[No extractable text found in this PDF.]"

    txt_path.write_text(text_content, encoding="utf-8")
    logger.info(f"Extracted text saved to: {txt_path}")

    return txt_path
