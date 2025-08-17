from typing import Callable, Coroutine, Any
from fastapi import WebSocket

from pydantic.types import SecretStr
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    BaseMessage,
    AIMessageChunk,
    ToolMessage,
    AIMessage,
)

from llm.base.inference import BaseInference
from llm.base.callbacks import CallBackHandler
from utils.vars import get_gemini_api_key
from utils.app_config import AppConfig


class GeminiInference(BaseInference):
    """Gemini Inference Engine."""

    def __init__(
        self,
        app_config: AppConfig = AppConfig.load_default(),
    ):
        self.app_config = app_config
        self.llm = ChatGoogleGenerativeAI(
            model=self.app_config.inference.inference_config.gemini.model,
            google_api_key=get_gemini_api_key(),
            temperature=self.app_config.inference.inference_config.gemini.temperature,
            max_output_tokens=self.app_config.inference.inference_config.gemini.max_tokens,
        )
        self.function_call_handler = None
        self.llm_with_tools = None

    def tools(self, tools: list[BaseTool]) -> "GeminiInference":
        """Set tools for the language model."""

        assert isinstance(
            self.llm, ChatGoogleGenerativeAI
        ), "LLM must be an instance of ChatOpenAI to bind tools."

        self.llm_with_tools = self.llm.bind_tools(tools)

        return self

    def tools_handler(
        self,
        tool_handler: Callable[[str, str, str], Coroutine[Any, Any, ToolMessage]],
    ) -> "GeminiInference":
        """Set Function Call handler for tools"""

        self.function_call_handler = tool_handler

        return self

    async def stream(
        self,
        websocket: WebSocket,
        messages: list[BaseMessage],
        max_depth: int = 5,
        depth: int = 0,
        response_str: str = "",
    ) -> str:
        """Recursively process tool calls and stream responses."""

        if depth >= max_depth:
            return response_str

        tool_calls_args = {}  # (tool_name, tool_id) -> args
        last_tool_name = ""
        last_tool_id = ""

        async for chunk in self.llm_with_tools.astream(messages, {"callbacks": [CallBackHandler(websocket)]}):  # type: ignore
            if isinstance(chunk, AIMessageChunk):
                if chunk.tool_calls:
                    for tool_call in chunk.tool_calls:
                        if tool_call["name"] and tool_call["id"]:
                            tool_calls_args[(tool_call["name"], tool_call["id"])] = ""
                            last_tool_name = tool_call["name"]
                            last_tool_id = tool_call["id"]

                if "tool_calls" in chunk.additional_kwargs:
                    for tool_call in chunk.additional_kwargs["tool_calls"]:
                        tool_calls_args[(last_tool_name, last_tool_id)] += tool_call[
                            "function"
                        ]["arguments"]

                if isinstance(chunk.content, str) and chunk.content:
                    response_str += chunk.content
                    await websocket.send_text(chunk.content)

        if not tool_calls_args:
            return response_str

        tool_messages = []
        assert self.function_call_handler is not None
        for (tool_name, tool_id), args in tool_calls_args.items():
            if tool_name and tool_id:
                tool_messages.append(
                    await self.function_call_handler(tool_id, tool_name, args)
                )

        next_messages = [AIMessage(content=response_str)] + tool_messages
        return await self.stream(
            websocket, messages + next_messages, max_depth, depth + 1, response_str
        )

    async def chat(self, messages: list[BaseMessage]) -> str:
        """Generate a response from the language model based on the provided messages."""

        if self.llm:
            response = await self.llm.ainvoke(messages)

            return (
                response.content
                if isinstance(response.content, str)
                else str(response.content)
            )

        return ""
