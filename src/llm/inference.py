from typing import Union, Callable, Optional, Coroutine, Any

from langchain_core.tools import BaseTool
from langchain_core.messages import ToolMessage

from llm.base.inference import BaseInference
from llm.local.inference import LocalInference
from llm.gemini.inference import GeminiInference
from llm.openai.inference import OpenAIInference
from utils.app_config import AppConfig, InferenceEngine


class Inference:
    def __init__(self, app_config: AppConfig = AppConfig.load_default()):
        self.app_config = app_config
        self.llm: Union[BaseInference, None] = None
        self.function_call_handler: Optional[
            Callable[[str, str, str], Coroutine[Any, Any, ToolMessage]]
        ] = None

        match self.app_config.inference.inference_engine:
            case InferenceEngine.LOCAL:
                self.llm = LocalInference()
            case InferenceEngine.GEMINI:
                self.llm = GeminiInference()
            case InferenceEngine.OPENAI:
                self.llm = OpenAIInference()
            case _:
                raise ValueError("Unknown inference engine")

    def with_tools(self, tools: list[BaseTool]) -> "Inference":
        """Add tools to the inference engine."""
        if self.llm is not None:
            self.llm.tools(tools)

        return self

    def with_tool_handler(
        self,
        tool_handler: Callable[[str, str, str], Coroutine[Any, Any, ToolMessage]],
    ) -> "Inference":
        """Add Function Call handler."""

        self.function_call_handler = tool_handler

        assert self.llm is not None

        self.llm.tools_handler(tool_handler)

        return self

    async def stream(self, websocket, chat_history) -> str:
        """Stream the response from the LLM."""
        if self.llm is not None:
            return await self.llm.stream(websocket, chat_history)
        else:
            raise ValueError("LLM instance is not initialized")

    async def chat(self, chat_history):
        """Perform a chat operation."""
        if self.llm is not None:
            return await self.llm.chat(chat_history)
        else:
            raise ValueError("LLM instance is not initialized")

    def get_llm(self) -> Union[BaseInference, None]:
        """Get the LLM instance."""
        return self.llm

