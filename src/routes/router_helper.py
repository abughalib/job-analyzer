from fastapi import WebSocket

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from llm.local.inference import LocalInference


class ConnectionManager:
    """WebSocket Connection Manager"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.chat_history: dict[WebSocket, list[BaseMessage]] = {}

    async def connect(self, websocket: WebSocket):
        """Handle websocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.chat_history[websocket] = [
            SystemMessage(content="You are a helpful assistant.")
        ]

    def disconnect(self, websocket: WebSocket):
        """Handle websocket disconnect"""
        self.active_connections.remove(websocket)
        del self.chat_history[websocket]

    async def broadcast(self, message: str):
        """Broadcast websocket message"""
        for connection in self.active_connections:
            await connection.send_text(message)

    async def handle_chat_completion(self, websocket: WebSocket, message: str):
        """Handle chat completion logic"""

        self.chat_history[websocket].append(HumanMessage(content=message))

        local_inference = LocalInference()

        await local_inference.stream(websocket, self.chat_history[websocket])
