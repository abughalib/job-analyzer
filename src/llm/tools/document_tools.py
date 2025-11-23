"""LangChain tools for document retrieval."""

import json
import logging

from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

from job_analyzer.document_storage.document_manager import get_document

logger = logging.getLogger(__name__)


@tool(
    description="Retrieve an uploaded document (resume, job description, etc.) by its document ID. Use this when the user references a document ID in their message."
)
async def get_uploaded_document_tool(document_id: str) -> str:
    """
    Retrieve an uploaded document by ID.

    Args:
        document_id (str): The UUID of the uploaded document.

    Returns:
        str: JSON with document content and metadata.
    """
    document = get_document(document_id)

    if document:
        return json.dumps(
            {
                "status": "found",
                "document_id": document.id,
                "filename": document.original_filename,
                "type": document.file_type,
                "content": document.extracted_text,
            }
        )
    else:
        return json.dumps(
            {
                "status": "not_found",
                "document_id": document_id,
                "error": "Document not found. Please check the ID.",
            }
        )


async def document_retrieval_call_handler(
    function_id: str, function_name: str, function_args: str
) -> ToolMessage:
    """
    Handle document retrieval tool calls.

    Args:
        function_id: The unique ID of the function call.
        function_name: The name of the function being called.
        function_args: JSON string of function arguments.

    Returns:
        ToolMessage: The result of the tool call.
    """
    try:
        json_args = json.loads(function_args) if function_args else {}

        match function_name:
            case "get_uploaded_document_tool":
                document_id = json_args.get("document_id", "")
                document = get_document(document_id)

                if document:
                    result = {
                        "status": "found",
                        "document_id": document.id,
                        "filename": document.original_filename,
                        "type": document.file_type,
                        "content": document.extracted_text,
                    }
                    return ToolMessage(
                        tool_call_id=function_id,
                        status="success",
                        content=json.dumps(result),
                    )
                else:
                    return ToolMessage(
                        tool_call_id=function_id,
                        status="error",
                        content=f"Document {document_id} not found",
                    )

    except Exception as e:
        logger.error(
            f"Error in document_retrieval_call_handler: {str(e)}", exc_info=True
        )
        return ToolMessage(
            tool_call_id=function_id,
            status="error",
            content=f"Error: {str(e)}",
        )

    return ToolMessage(
        tool_call_id=function_id,
        status="error",
        content=f"No tool with name: {function_name}",
    )
