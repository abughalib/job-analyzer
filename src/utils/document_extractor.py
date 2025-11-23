"""Unified document text extractor supporting PDF, DOCX, and TXT formats."""

import logging
from pathlib import Path

from utils.pdf_extractor import extract_text_from_pdf
from utils.docx_extractor import extract_text_from_docx

logger = logging.getLogger(__name__)


async def extract_document_text(file_path: str | Path) -> str:
    """
    Extract text from PDF, DOCX, or TXT files.

    Args:
        file_path: Path to the document file.

    Returns:
        Extracted text content.

    Raises:
        ValueError: If file type is not supported.
        RuntimeError: If extraction fails.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()

    try:
        match suffix:
            case ".pdf":
                logger.debug(f"Extracting text from PDF: {file_path.name}")
                return extract_text_from_pdf(file_path)

            case ".docx":
                logger.debug(f"Extracting text from DOCX: {file_path.name}")
                return extract_text_from_docx(file_path)

            case ".txt":
                logger.debug(f"Reading text from TXT: {file_path.name}")
                return file_path.read_text(encoding="utf-8")

            case _:
                raise ValueError(
                    f"Unsupported file type: {suffix}. Supported formats: .pdf, .docx, .txt"
                )

    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {str(e)}", exc_info=True)
        raise RuntimeError(f"Document extraction failed: {str(e)}")
