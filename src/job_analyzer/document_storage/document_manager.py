"""Document storage manager for handling uploaded files."""

import uuid
import logging
from pathlib import Path
from typing import Optional, Dict
import xxhash

from fastapi import UploadFile

from utils.vars import get_app_path
from utils.constants import UPLOADED_FILE_FOLDER
from utils.document_extractor import extract_document_text
from utils.document_summarizer import prepare_document_for_analysis
from job_analyzer.document_storage.models import UploadedDocument

logger = logging.getLogger(__name__)

# In-memory storage for documents For now
_document_store: Dict[str, UploadedDocument] = {}


async def save_uploaded_document(
    file: UploadFile,
    doc_type: str = "other",
    session_id: Optional[str] = None,
    summarize: bool = True,
) -> UploadedDocument:
    """
    Save an uploaded document and extract its text.

    Args:
        file: The uploaded file
        doc_type: Type of document (resume, job_description, other)
        session_id: Optional session identifier
        summarize: Whether to summarize the document if it's too long

    Returns:
        UploadedDocument with metadata and extracted text
    """
    try:
        logger.debug(
            f"Starting document upload: {file.filename}, type: {doc_type}, session: {session_id}"
        )
        # Read file content
        contents = await file.read()
        file_hash = xxhash.xxh64(contents).hexdigest()

        # Check if already exists
        existing_doc = _find_document_by_hash(file_hash)
        if existing_doc:
            logger.info(f"Document already exists with hash {file_hash}")
            return existing_doc

        # Determine file format
        filename = file.filename or "unknown"
        file_extension = Path(filename).suffix.lower().lstrip(".")
        if file_extension not in ["pdf", "docx", "txt"]:
            raise ValueError(f"Unsupported file format: {file_extension}")

        # Save to disk temporarily
        upload_dir = get_app_path().joinpath(UPLOADED_FILE_FOLDER)
        upload_dir.mkdir(parents=True, exist_ok=True)

        temp_filename = f"{file_hash}.{file_extension}"
        temp_path = upload_dir / temp_filename

        with open(temp_path, "wb") as f:
            f.write(contents)

        logger.info(f"Saved file to {temp_path}")

        # Extract text
        extracted_text = await extract_document_text(temp_path)

        # Summarize if needed
        if summarize:
            extracted_text = await prepare_document_for_analysis(
                extracted_text, doc_type=doc_type
            )

        # Create document record
        doc_id = str(uuid.uuid4())
        document = UploadedDocument(
            id=doc_id,
            file_hash=file_hash,
            original_filename=filename,
            file_type=doc_type,
            file_format=file_extension,
            extracted_text=extracted_text,
            session_id=session_id,
            metadata={"file_path": str(temp_path)},
        )

        # Store in memory
        _document_store[doc_id] = document
        logger.info(f"Stored document {doc_id} ({doc_type})")

        return document

    except Exception as e:
        logger.error(f"Error saving document: {str(e)}", exc_info=True)
        raise


async def save_text_document(
    text: str,
    doc_type: str = "other",
    filename: str = "pasted_text.txt",
    session_id: Optional[str] = None,
    summarize: bool = True,
) -> UploadedDocument:
    """
    Save pasted/typed text as a document.

    Args:
        text: The text content
        doc_type: Type of document (resume, job_description, other)
        filename: Logical filename for the text
        session_id: Optional session identifier
        summarize: Whether to summarize if too long

    Returns:
        UploadedDocument with metadata
    """
    try:
        logger.debug(
            f"Starting text document save. Type: {doc_type}, filename: {filename}, session: {session_id}"
        )
        # Create hash of text
        text_hash = xxhash.xxh64(text.encode()).hexdigest()

        # Check if already exists
        existing_doc = _find_document_by_hash(text_hash)
        if existing_doc:
            logger.info(f"Text document already exists with hash {text_hash}")
            return existing_doc

        # Summarize if needed
        processed_text = text
        if summarize:
            processed_text = await prepare_document_for_analysis(
                text, doc_type=doc_type
            )

        # Create document record
        doc_id = str(uuid.uuid4())
        document = UploadedDocument(
            id=doc_id,
            file_hash=text_hash,
            original_filename=filename,
            file_type=doc_type,
            file_format="text",
            extracted_text=processed_text,
            session_id=session_id,
            metadata={"source": "paste"},
        )

        # Store in memory
        _document_store[doc_id] = document
        logger.info(f"Stored text document {doc_id} ({doc_type})")

        return document

    except Exception as e:
        logger.error(f"Error saving text document: {str(e)}", exc_info=True)
        raise


def get_document(doc_id: str) -> Optional[UploadedDocument]:
    """
    Retrieve a document by ID.

    Args:
        doc_id: Document ID

    Returns:
        UploadedDocument if found, None otherwise
    """

    logger.debug(f"Retrieving document with ID: {doc_id}")
    doc = _document_store.get(doc_id)

    if doc:
        logger.debug(f"Document found: {doc.original_filename}")
    else:
        logger.debug("Document not found")
    return doc


def _find_document_by_hash(file_hash: str) -> Optional[UploadedDocument]:
    """Find a document by its file hash."""
    for doc in _document_store.values():
        if doc.file_hash == file_hash:
            return doc
    return None


def delete_document(doc_id: str) -> bool:
    """
    Delete a document.

    Args:
        doc_id: Document ID

    Returns:
        True if deleted, False if not found
    """
    if doc_id in _document_store:
        doc = _document_store.pop(doc_id)

        # Delete file if it exists
        if "file_path" in doc.metadata:
            try:
                file_path = Path(doc.metadata["file_path"])
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file: {str(e)}")

        logger.info(f"Deleted document {doc_id}")
        return True
    return False
