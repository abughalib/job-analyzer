from fastapi import WebSocket

from pydantic.types import SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage

from utils.app_config import AppConfig


class LocalInference:
    """Local inference using a language model."""

    def __init__(self, app_config: AppConfig = AppConfig.load_default()):
        self.app_config = app_config
        self.llm = ChatOpenAI(
            base_url=self.app_config.inference.inference_config.api_base,
            model=self.app_config.inference.inference_config.model,
            temperature=self.app_config.inference.inference_config.temperature,
            api_key=SecretStr("no-key"),  # Local inference does not require an API key
        )

    async def stream(self, websocket: WebSocket, messages: list[BaseMessage]) -> str:
        """Stream responses from the language model to a WebSocket."""

        response_str: str = ""

        async for chunk in self.llm.astream(messages):
            if isinstance(chunk.content, str):  # type: ignore
                await websocket.send_text(chunk.content)
                response_str += chunk.content
            else:
                # Unknown Chunk Type
                print(f"Unknown chunk type: {str(chunk)}")

        return response_str

    def chat(self, messages: list[BaseMessage]) -> str:
        """Generate a response from the language model based on the provided messages."""
        response = self.llm.invoke(messages)

        print(f"Response: ", str(response))

        return ""
