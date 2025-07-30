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

router = APIRouter()
manager = ConnectionManager()  # Create a single instance


@router.get("", tags=["Home"])
async def get_home():
    return {"message": "Hi There!"}


@router.post("/chat", tags=["Chat"])
async def chat():

    return {"endpoint": "Chat EndPoint"}


@router.post("/add_layoff_data_csv", tags=["Add Data"])
async def upload_layoff_data_csv(file: UploadFile):
    """
    Upload Layoff data csv file
    """

    uploaded_result = await handle_layoff_file_upload(file)

    match uploaded_result:
        case APISTATUS.OK:
            return {"status": "File Uploaded"}
        case APISTATUS.DUPLICATE:
            return {"status": "File already exists"}
        case APISTATUS.PERMISSIONERROR:
            return {"status": "File Permission Error"}

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/layoffs/")
async def read_recent_layoffs(days: int = 7, limit: int = 10):
    """
    API endpoint to get recent layoffs.
    It calls the function which uses the session from the context variable.
    """
    try:
        layoffs = await get_recent_layoff(days=days, limit=limit)
        return layoffs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):

    try:
        await manager.connect(websocket)
        while True:
            data = await websocket.receive_text()
            await manager.handle_chat_completion(websocket, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("Client left the chat")
    except Exception as e:
        manager.disconnect(websocket)
        await manager.broadcast(f"Error: {str(e)}")
