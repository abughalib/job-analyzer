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
            data = await websocket.receive_text()
            logger.debug(
                f"Received message from client {client_id}: {data[:100]}..."
            )  # Log first 100 chars
            await manager.handle_chat_completion(websocket, data)

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
