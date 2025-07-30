import json
from typing import Optional

from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

from job_analyzer.database.models import LayOff
from job_analyzer.database.layoff_db import get_recent_layoff, get_field_unique_values


@tool(description="Get `get_recent_layoff_tool` fields possible values.")
async def get_recent_layoff_tool_fields(field_name: str) -> list[str]:
    """Retrieve possible values for the fields of `get_recent_layoff_tool`."""
    return await get_field_unique_values(field_name)


@tool(description="Get recent layoffs in Tech industry.")
async def get_recent_layoff_tool(
    company_name: Optional[str] = None,
    days_to_look_back: Optional[int] = 5,
    hq_location: Optional[str] = None,
    tech_industry_type: Optional[str] = None,
    layoff_date: Optional[str] = None,
    layoff_stage: Optional[str] = None,
    country: Optional[str] = None,
    offset: int = 0,
):
    """Retrieve recent layoff records based on various filters.
    Args:
        company_name (Optional[str]): Name of the company.
        days_to_look_back (Optional[int]): Number of days to look back for layoffs.
        hq_location (Optional[str]): Headquarters location of the company.
        tech_industry_type (Optional[str]): Industry of the company, i.e. Transportation, Finance.
        layoff_date (Optional[str]): Specific date to filter layoffs.
        layoff_stage (Optional[str]): Stage of the layoff process.
        country (Optional[str]): Country where the layoffs occurred.
        offset (int): Offset for pagination, limit is 20.
    Returns:
        str: A markdown representation of the recent layoffs.
    """
    recent_lay_off = await get_recent_layoff(
        company_name=company_name,
        days=days_to_look_back,
        hq_location=hq_location,
        industry=tech_industry_type,
        date=layoff_date,
        stage=layoff_stage,
        country=country,
        offset=offset,
    )

    return LayOff.as_context(recent_lay_off)


async def layoff_call_handler(
    function_id: str, function_name: str, function_args: str
) -> ToolMessage:

    match function_name:
        case "get_recent_layoff_tool_fields":
            json_args = json.loads(function_args)
            if json_args:
                field_name = json_args["field_name"]
                return ToolMessage(
                    tool_call_id=function_id,
                    content=json.dumps(get_recent_layoff_tool(field_name)),
                    status="success",
                )
            else:
                return ToolMessage(
                    tool_call_id=function_id,
                    content="Cannot Parse function call argument",
                    status="error",
                )
        case "get_recent_layoff_tool":
            josn_args = json.loads(str(function_args))
            recent_lay_off = await get_recent_layoff()
            return ToolMessage(
                tool_call_id=function_id,
                content=LayOff.as_context(recent_lay_off),
                status="success",
            )
    raise NotImplementedError("Method not implemented")
