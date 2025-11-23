"""Document storage models for uploaded resumes and job descriptions."""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class UploadedDocument(BaseModel):
    """Model for uploaded document metadata."""

    id: str = Field(description="Unique document ID (UUID)")
    file_hash: str = Field(description="Hash of file content for deduplication")
    original_filename: str = Field(description="Original filename")
    file_type: Literal["resume", "job_description", "other"] = Field(
        description="Type of document"
    )
    file_format: Literal["pdf", "docx", "txt", "text"] = Field(
        description="File format"
    )
    extracted_text: str = Field(description="Extracted text content")
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = Field(None, description="Optional session identifier")
    metadata: Optional[dict] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
