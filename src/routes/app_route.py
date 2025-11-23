import logging
import json as json_lib
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    UploadFile,
    status,
)

from routes.router_helper import ConnectionManager, handle_layoff_file_upload
from job_analyzer.database.layoff_db import get_recent_layoff
from routes.models import APISTATUS

logger = logging.getLogger(__name__)

router = APIRouter()
manager = ConnectionManager()  # Create a single instance


@router.get("", tags=["Home"])
async def get_home():
    logger.debug("Handling home route request")
    return {"message": "Hi There!"}


@router.post("/chat", tags=["Chat"])
async def chat():
    logger.debug("Handling POST /chat request")
    return {"endpoint": "Chat EndPoint"}


@router.post("/add_layoff_data_csv", tags=["Add Data"])
async def upload_layoff_data_csv(file: UploadFile):
    """
    Upload Layoff data csv file
    """
    logger.info(f"Received layoff data CSV upload request: {file.filename}")

    try:
        uploaded_result = await handle_layoff_file_upload(file)

        match uploaded_result:
            case APISTATUS.OK:
                logger.info(
                    f"Successfully uploaded and processed file: {file.filename}"
                )
                return {"status": "File Uploaded"}
            case APISTATUS.DUPLICATE:
                logger.warning(f"Duplicate file detected: {file.filename}")
                return {"status": "File already exists"}
            case APISTATUS.PERMISSIONERROR:
                logger.error(f"Permission error while handling file: {file.filename}")
                return {"status": "File Permission Error"}

        logger.error(f"Unexpected upload result status for file: {file.filename}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(
            f"Error processing upload for {file.filename}: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/upload/resume", tags=["Documents"])
async def upload_resume(file: UploadFile, session_id: str | None = None):
    """
    Upload a resume file (PDF, DOCX, or TXT).
    """
    logger.info(f"Received resume upload: {file.filename}")

    try:
        from job_analyzer.document_storage.document_manager import (
            save_uploaded_document,
        )

        document = await save_uploaded_document(
            file, doc_type="resume", session_id=session_id
        )

        return {
            "status": "success",
            "document_id": document.id,
            "filename": document.original_filename,
            "text_length": len(document.extracted_text),
        }

    except ValueError as e:
        logger.warning(f"Invalid file upload: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/upload/job_description", tags=["Documents"])
async def upload_job_description(file: UploadFile, session_id: str | None = None):
    """
    Upload a job description file (PDF, DOCX, or TXT).
    """
    logger.info(f"Received job description upload: {file.filename}")

    try:
        from job_analyzer.document_storage.document_manager import (
            save_uploaded_document,
        )

        document = await save_uploaded_document(
            file, doc_type="job_description", session_id=session_id
        )

        return {
            "status": "success",
            "document_id": document.id,
            "filename": document.original_filename,
            "text_length": len(document.extracted_text),
        }

    except ValueError as e:
        logger.warning(f"Invalid file upload: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading job description: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/upload/text", tags=["Documents"])
async def upload_text(
    text: str,
    doc_type: str = "other",
    filename: str = "pasted_text.txt",
    session_id: str | None = None,
):
    """
    Upload text content (copy/paste, certifications, skills list, etc.).
    """
    logger.info(f"Received text upload: {filename} ({doc_type})")

    try:
        from job_analyzer.document_storage.document_manager import save_text_document

        document = await save_text_document(
            text, doc_type=doc_type, filename=filename, session_id=session_id
        )

        return {
            "status": "success",
            "document_id": document.id,
            "filename": document.original_filename,
            "text_length": len(document.extracted_text),
        }

    except Exception as e:
        logger.error(f"Error uploading text: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/layoffs/")
async def read_recent_layoffs(days: int = 7, limit: int = 10):
    """
    API endpoint to get recent layoffs.
    It calls the function which uses the session from the context variable.
    """
    logger.info(f"Fetching recent layoffs: days={days}, limit={limit}")
    try:
        layoffs = await get_recent_layoff(days=days, limit=limit)
        logger.debug(f"Successfully retrieved {len(layoffs)} layoff records")
        return layoffs
    except Exception as e:
        logger.error(f"Error fetching recent layoffs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    client_id = id(websocket)  # Use websocket id for tracking connections


import logging
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    UploadFile,
    status,
)

from routes.router_helper import ConnectionManager, handle_layoff_file_upload
from job_analyzer.database.layoff_db import get_recent_layoff
from routes.models import APISTATUS

logger = logging.getLogger(__name__)

router = APIRouter()
manager = ConnectionManager()  # Create a single instance


@router.get("", tags=["Home"])
async def get_home():
    logger.debug("Handling home route request")
    return {"message": "Hi There!"}


@router.post("/chat", tags=["Chat"])
async def chat():
    logger.debug("Handling POST /chat request")
    return {"endpoint": "Chat EndPoint"}


@router.post("/add_layoff_data_csv", tags=["Add Data"])
async def upload_layoff_data_csv(file: UploadFile):
    """
    Upload Layoff data csv file
    """
    logger.info(f"Received layoff data CSV upload request: {file.filename}")

    try:
        uploaded_result = await handle_layoff_file_upload(file)

        match uploaded_result:
            case APISTATUS.OK:
                logger.info(
                    f"Successfully uploaded and processed file: {file.filename}"
                )
                return {"status": "File Uploaded"}
            case APISTATUS.DUPLICATE:
                logger.warning(f"Duplicate file detected: {file.filename}")
                return {"status": "File already exists"}
            case APISTATUS.PERMISSIONERROR:
                logger.error(f"Permission error while handling file: {file.filename}")
                return {"status": "File Permission Error"}

        logger.error(f"Unexpected upload result status for file: {file.filename}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(
            f"Error processing upload for {file.filename}: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/upload/resume", tags=["Documents"])
async def upload_resume(file: UploadFile, session_id: str | None = None):
    """
    Upload a resume file (PDF, DOCX, or TXT).
    """
    logger.info(f"Received resume upload: {file.filename}")

    try:
        from job_analyzer.document_storage.document_manager import (
            save_uploaded_document,
        )

        document = await save_uploaded_document(
            file, doc_type="resume", session_id=session_id
        )

        return {
            "status": "success",
            "document_id": document.id,
            "filename": document.original_filename,
            "text_length": len(document.extracted_text),
        }

    except ValueError as e:
        logger.warning(f"Invalid file upload: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/upload/job_description", tags=["Documents"])
async def upload_job_description(file: UploadFile, session_id: str | None = None):
    """
    Upload a job description file (PDF, DOCX, or TXT).
    """
    logger.info(f"Received job description upload: {file.filename}")

    try:
        from job_analyzer.document_storage.document_manager import (
            save_uploaded_document,
        )

        document = await save_uploaded_document(
            file, doc_type="job_description", session_id=session_id
        )

        return {
            "status": "success",
            "document_id": document.id,
            "filename": document.original_filename,
            "text_length": len(document.extracted_text),
        }

    except ValueError as e:
        logger.warning(f"Invalid file upload: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading job description: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/upload/text", tags=["Documents"])
async def upload_text(
    text: str,
    doc_type: str = "other",
    filename: str = "pasted_text.txt",
    session_id: str | None = None,
):
    """
    Upload text content (copy/paste, certifications, skills list, etc.).
    """
    logger.info(f"Received text upload: {filename} ({doc_type})")

    try:
        from job_analyzer.document_storage.document_manager import save_text_document

        document = await save_text_document(
            text, doc_type=doc_type, filename=filename, session_id=session_id
        )

        return {
            "status": "success",
            "document_id": document.id,
            "filename": document.original_filename,
            "text_length": len(document.extracted_text),
        }

    except Exception as e:
        logger.error(f"Error uploading text: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/layoffs/")
async def read_recent_layoffs(days: int = 7, limit: int = 10):
    """
    API endpoint to get recent layoffs.
    It calls the function which uses the session from the context variable.
    """
    logger.info(f"Fetching recent layoffs: days={days}, limit={limit}")
    try:
        layoffs = await get_recent_layoff(days=days, limit=limit)
        logger.debug(f"Successfully retrieved {len(layoffs)} layoff records")
        return layoffs
    except Exception as e:
        logger.error(f"Error fetching recent layoffs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    client_id = id(websocket)  # Use websocket id for tracking connections
    logger.info(f"New WebSocket connection request from client {client_id}")

    try:
        await manager.connect(websocket)
        logger.info(f"Client {client_id} connected successfully")

        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received WebSocket message: {data[:100]}...")

                # Parse message - support both plain text and JSON with document IDs
                message_text = data
                resume_id = None
                jd_id = None

                try:
                    message_data = json_lib.loads(data)
                    if isinstance(message_data, dict):
                        message_text = message_data.get("message", data)
                        resume_id = message_data.get("resume_id")
                        jd_id = message_data.get("jd_id")
                        logger.debug(
                            f"Parsed document IDs - resume: {resume_id}, jd: {jd_id}"
                        )
                except json_lib.JSONDecodeError:
                    # Plain text message, use as-is
                    pass

                # Inject document context if IDs provided
                if resume_id or jd_id:
                    from job_analyzer.document_storage.document_manager import (
                        get_document,
                    )

                    context_parts = []

                    if resume_id:
                        resume_doc = await get_document(resume_id)
                        if resume_doc:
                            context_parts.append(
                                f"[RESUME CONTENT]\n{resume_doc.extracted_text}\n[END RESUME]"
                            )
                            logger.info(
                                f"Injected resume document: {resume_doc.original_filename}"
                            )
                        else:
                            logger.warning(f"Resume document {resume_id} not found")

                    if jd_id:
                        jd_doc = await get_document(jd_id)
                        if jd_doc:
                            context_parts.append(
                                f"[JOB DESCRIPTION]\n{jd_doc.extracted_text}\n[END JOB DESCRIPTION]"
                            )
                            logger.info(
                                f"Injected JD document: {jd_doc.original_filename}"
                            )
                        else:
                            logger.warning(f"JD document {jd_id} not found")

                    # Prepend document context to message
                    if context_parts:
                        message_text = (
                            "\n\n".join(context_parts) + "\n\n" + message_text
                        )

                await manager.handle_chat_completion(websocket, message_text)

            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
                manager.disconnect(websocket)
                break
            except Exception as e:
                logger.error(
                    f"Error in WebSocket communication: {str(e)}", exc_info=True
                )
                manager.disconnect(websocket)
                await manager.broadcast(f"Error: {str(e)}")
                break

    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
        manager.disconnect(websocket)
        await manager.broadcast("Client left the chat")

    except Exception as e:
        logger.error(
            f"Error in WebSocket connection for client {client_id}: {str(e)}",
            exc_info=True,
        )
        manager.disconnect(websocket)
        await manager.broadcast(f"Error: {str(e)}")
