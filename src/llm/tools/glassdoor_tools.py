import time
import json
from typing import Optional
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

from job_analyzer.external_api.glassdoor import get_salary_data


@tool(
    description="Retrieve salary data for a specific job based on company, location, job function, and experience."
)
async def search_job_salary_tool(
    company_name: str,
    location: Optional[str] = None,
    job_function: Optional[str] = None,
    year_of_experience: Optional[str] = None,
    limit: int = 10,
    page: int = 1,
    sort: str = "POPULAR",
) -> str:
    """
    Retrieve salary data for a given job based on specified criteria from Glassdoor.
    Args:
        company_name (str): The name of the company.
        location (Optional[str], optional): The location for which to retrieve salary data. Defaults to None.
        job_function (Optional[str], optional): The job function to search for. Defaults to None.
        year_of_experience (Optional[str], optional): The year of experience for the job. Defaults to None.
        limit (int, optional): The maximum number of results to return per page. Defaults to 10.
        page (int, optional): The page number to retrieve. Defaults to 1.
        sort (str, optional): The sorting order of the results ('POPULAR', 'HIGH_PAY', 'LOW_PAY'). Defaults to "POPULAR".

    Returns:
        str: A JSON string containing the salary data retrieved from Glassdoor.  Returns an empty JSON object if no results are found or an error occurs.
    """
    salary_data = await get_salary_data(
        company_name,
        location,
        job_function,
        year_of_experience,
        limit,
        page,
        sort,
    )

    return json.dumps(salary_data.as_context())


async def glassdoor_call_handler(
    function_id: str, function_name: str, function_args: str
) -> ToolMessage:
    """Handle Glassdoor related tool calls"""

    match function_name:
        case "search_job_salary_tool":
            json_args = json.loads(function_args) if function_args else json.loads("{}")
            company_name = json_args["company_name"]
            location = json_args.get("location", None)
            job_function = json_args.get("job_function", None)
            year_of_experience = json_args.get("year_of_experience", None)
            page = json_args.get("page", 1)
            sort_by = json_args.get("sort", "popularity")
            limit = json_args.get("limit", 5)

            recent_news = await get_salary_data(
                company_name,
                location,
                job_function,
                year_of_experience,
                limit,
                page,
                sort_by,
            )

            return ToolMessage(
                tool_call_id=function_id,
                status="success",
                content=json.dumps(recent_news.as_context()),
            )

    return ToolMessage(
        tool_call_id=function_id,
        content=f"No tool with name: {function_name}",
        status="error",
    )
