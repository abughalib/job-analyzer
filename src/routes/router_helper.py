from pathlib import Path

import xxhash
from fastapi import WebSocket, UploadFile
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from routes.models import APISTATUS
from utils.vars import get_app_path
from llm.inference import Inference
from llm.tools.layoff_tools import (
    get_recent_layoff_tool,
    get_recent_layoff_tool_fields,
)
from job_analyzer.database.models import LayOff
from job_analyzer.database.layoff_db import add_layoff_bulk
from llm.tools.tool_helper import functional_call_handler as tool_handler
from utils.constants import UPLOADED_FILE_FOLDER


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

        inference = (
            Inference()
            .with_tools([get_recent_layoff_tool, get_recent_layoff_tool_fields])
            .with_tool_handler(tool_handler)
        )

        await inference.stream(websocket, self.chat_history[websocket])


async def handle_layoff_file_upload(file: UploadFile) -> APISTATUS:
    contents = await file.read()

    file_hash = xxhash.xxh64(contents).hexdigest()

    file_extension = Path(file.filename or "abc.csv").suffix

    upload_path = (
        get_app_path()
        .joinpath(UPLOADED_FILE_FOLDER)
        .joinpath(f"temp_{file_hash}.{file_extension}")
    )

    if upload_path.exists():
        return APISTATUS.DUPLICATE

    try:
        with open(upload_path, "wb") as f:
            f.write(contents)

    except PermissionError:
        return APISTATUS.PERMISSIONERROR

    layoff_parsed = LayOff.from_csv(upload_path)

    await add_layoff_bulk(layoff_parsed)

    return APISTATUS.OK
