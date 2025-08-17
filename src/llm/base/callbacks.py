from typing import Any
from uuid import UUID
from fastapi import WebSocket
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage


class CallBackHandler(BaseCallbackHandler):

    def __init__(self, websocket: WebSocket):
        super().__init__()
        self.websocket = websocket

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        print("Tool started: ", serialized)

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        print("Tool ended: ", output)
