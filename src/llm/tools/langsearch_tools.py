import json

from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

from job_analyzer.external_api.langsearch import get_langsearch


@tool(
    description="Performs a general web search and returns summarized results including headlines and article summaries based on a search keyword and result limit."
)
async def search_recent_web_content_tool(keyword: str, limit: int = 5):
    """
    Perform a web search and retrieve summarized recent content based on a keyword.

    Args:
        keyword (str): The term or phrase to search for. This is typically a topic, name, or question.
        limit (int, optional): Maximum number of results to return. Default is 5.
            Adjust this to retrieve more or fewer search results.

    Returns:
        str: A JSON-formatted string containing a list of summarized search results.
            Each result includes a headline and a brief summary of the content.
    """

    langsearch_result = await get_langsearch(keyword, limit)

    return json.dumps(langsearch_result.as_context(limit))


async def langsearch_call_handler(
    function_id: str, function_name: str, function_args: str
) -> ToolMessage:
    """Handle langsearch related tool calls"""

    match function_name:
        case "search_recent_web_content":
            json_args = json.loads(str(function_args))
            keyword = json_args["keyword"]
            limit = json_args.get("limit", 5)
            
            # Clean Keyword to remove special characters, quotes, and spaces
            keyword = keyword.replace('"', "").replace("'", "").replace(" ", "")

            langsearch_result = await get_langsearch(keyword, limit)

            return ToolMessage(
                tool_call_id=function_id,
                status="success",
                content=json.dumps(langsearch_result.as_context(limit)),
            )

    return ToolMessage(
        tool_call_id=function_id,
        content=f"No tool with name: {function_name}",
        status="error",
    )
