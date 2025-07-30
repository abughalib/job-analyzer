from langchain_core.messages import ToolMessage

from llm.tools.layoff_tools import layoff_call_handler


async def functional_call_handler(
    function_id: str, function_name: str, function_args: str
) -> ToolMessage:

    if "layoff" in function_name:
        return await layoff_call_handler(function_id, function_name, function_args)
    else:
        raise NotImplementedError("Not Implemented")
