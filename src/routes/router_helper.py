from fastapi import WebSocket


class ConnectionManager:
    """WebSocket Connection Manager"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Handle websocket connection"""
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Handle websocket disconnect"""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """Broadcast websocket message"""
        for connection in self.active_connections:
            await connection.send_text(message)


async def handle_chat_completion(websocket: WebSocket):
    pass
