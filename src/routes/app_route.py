from fastapi import APIRouter, WebSocket

from routes.router_helper import ConnectionManager


router = APIRouter()


@router.get("", tags=['Home'])
async def get_home():
    return {"message": "Hi There!"}


@router.post("/chat", tags=['Chat'])
async def chat():

    return {"endpoint": "Chat EndPoint"}


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):

    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message was: {data}")
