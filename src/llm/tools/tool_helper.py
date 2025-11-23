from langchain_core.messages import ToolMessage

from llm.tools.google_search_tools import google_search_call_handler
from llm.tools.document_tools import document_retrieval_call_handler
from llm.tools.langsearch_tools import langsearch_call_handler
from llm.tools.glassdoor_tools import glassdoor_call_handler
from llm.tools.layoff_tools import layoff_call_handler
from llm.tools.news_tools import news_call_handler
from llm.tools.analysis_tools import analysis_call_handler


async def functional_call_handler(
    function_id: str, function_name: str, function_args: str
) -> ToolMessage:

    if "layoff" in function_name:
        return await layoff_call_handler(function_id, function_name, function_args)
    elif "news" in function_name:
        return await news_call_handler(function_id, function_name, function_args)
    elif "web" in function_name:
        return await langsearch_call_handler(function_id, function_name, function_args)
    elif "google" in function_name:
        return await google_search_call_handler(
            function_id, function_name, function_args
        )
    elif "glassdoor" in function_name:
        return await glassdoor_call_handler(function_id, function_name, function_args)
    elif "analyze" in function_name:
        return await analysis_call_handler(function_id, function_name, function_args)
    elif "document" in function_name or "get_uploaded" in function_name:
        return await document_retrieval_call_handler(
            function_id, function_name, function_args
        )
    else:
        return ToolMessage(
            tool_call_id=function_id,
            content=f"No tool with name: {function_name}",
            status="error",
        )
