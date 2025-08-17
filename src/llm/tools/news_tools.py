import time
import json
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

from job_analyzer.external_api.news_api import get_recent_news


@tool(description="Search popular or latest general news articles using a keyword. Not limited to tech or layoffs.")
async def search_recent_news_tool(
    keyword: str,
    from_date: str = time.strftime(
        "%Y-%m-%d", time.localtime(time.time() - 7 * 24 * 60 * 60)
    ),
    sort_by: str = "popularity",
    limit: int = 5,
) -> str:
    """
    Retrieve recent news articles based on the provided keyword.

    Args:
        keyword (str): The search term or phrase to look for in news articles.
        from_date (str): A string representing the start date for which news should be retrieved Format: (YYYY-MM-DD). Default is 7 from today.
        sort_by (str): Criteria by which results are sorted, e.g., 'popularity', 'date'. Default is 'popularity'.
        limit (int): The number of articles to return in the search result. Default is 5.

    Returns:
        str: A string containing a summary or the content of recent news based on the given parameters.

    """
    recent_news = await get_recent_news(keyword, from_date, sort_by)

    return json.dumps(recent_news.as_context(limit))


async def news_call_handler(
    function_id: str, function_name: str, function_args: str
) -> ToolMessage:
    """Handle news related tool calls"""

    match function_name:
        case "search_recent_news_tool":
            json_args = json.loads(function_args) if function_args else json.loads("{}")
            keyword = json_args["keyword"]
            from_date = json_args.get(
                "from_date", time.localtime(time.time() - 7 * 24 * 60 * 60)
            )
            sort_by = json_args.get("sort_by", "popularity")
            limit = json_args.get("limit", 5)

            recent_news = await get_recent_news(keyword, from_date, sort_by)

            return ToolMessage(
                tool_call_id=function_id,
                status="success",
                content=json.dumps(recent_news.as_context(limit)),
            )

    return ToolMessage(
        tool_call_id=function_id,
        content=f"No tool with name: {function_name}",
        status="error",
    )
