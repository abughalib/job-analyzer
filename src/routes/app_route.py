from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from routes.router_helper import ConnectionManager


router = APIRouter()
manager = ConnectionManager()  # Create a single instance


@router.get("", tags=["Home"])
async def get_home():
    return {"message": "Hi There!"}


@router.post("/chat", tags=["Chat"])
async def chat():

    return {"endpoint": "Chat EndPoint"}


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
