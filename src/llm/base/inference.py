from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain.tools import BaseTool


class BaseInference:
    """Base class for inference engines."""

    def __init__(self):
        self.llm: Optional[BaseChatModel] = None

    def tools(self, tools: list[BaseTool]) -> "BaseInference":
        """Set tools for the language model."""

        raise NotImplementedError("This method should be implemented by subclasses.")

    async def stream(self, websocket, messages: list[BaseMessage]) -> str:
        """Stream the response from the language model."""

        raise NotImplementedError("This method should be implemented by subclasses.")

    async def chat(self, messages: list[BaseMessage]) -> str:
        """Handle chat completion logic."""

        raise NotImplementedError("This method should be implemented by subclasses.")

    def get_llm(self) -> Optional[BaseChatModel]:
        return self.llm
