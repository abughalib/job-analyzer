"""LangChain tools for job description and resume analysis."""

import json
import logging

from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

from job_analyzer.external_api.llm_analysis import (
    analyze_job_description_api,
    review_resume_api,
    calculate_fit_score_api,
)

logger = logging.getLogger(__name__)


@tool(
    description="Analyzes a job description to extract key information such as role, skills, experience, location, and compensation."
)
async def analyze_job_description_tool(jd_text: str) -> str:
    """
    Analyze a job description to extract structured information.

    Args:
        jd_text (str): The complete text of the job description to analyze.

    Returns:
        str: A JSON-formatted string containing extracted information including
            role, skills, experience, location, compensation, and company profile.
    """
    result = await analyze_job_description_api(jd_text)
    return json.dumps(result.as_context())


@tool(
    description="Reviews a resume against a specific job description, identifying strengths, gaps, and providing actionable suggestions for improvement."
)
async def analyze_resume_tool(resume_text: str) -> str:
    """
    Review a resume against a job description.

    Args:
        resume_text (str): The complete text of the resume to review.
        jd_text (str): The complete text of the job description to compare against.

    Returns:
        str: A JSON-formatted string containing strengths, gaps, suggestions,
            and an overall match summary.
    """
    result = await review_resume_api(resume_text)
    return json.dumps(result.as_context())


@tool(
    description="Calculates a fit score (0-100) for a candidate based on their resume and a job description, with confidence level and detailed explanation."
)
async def analyze_candidate_fit_tool(resume_text: str, jd_text: str) -> str:
    """
    Calculate a candidate's fit score for a role.

    Args:
        resume_text (str): The complete text of the candidate's resume.
        jd_text (str): The complete text of the job description.

    Returns:
        str: A JSON-formatted string containing the fit score (0-100),
            confidence level, and a detailed explanation.
    """
    result = await calculate_fit_score_api(resume_text, jd_text)
    return json.dumps(result.as_context())


async def analysis_call_handler(
    function_id: str, function_name: str, function_args: str
) -> ToolMessage:
    """
    Handle all analysis-related tool calls.

    Args:
        function_id: The unique ID of the function call.
        function_name: The name of the function being called.
        function_args: JSON string of function arguments.

    Returns:
        ToolMessage: The result of the tool call.
    """
    try:
        json_args = json.loads(function_args) if function_args else {}

        match function_name:
            case "analyze_job_description_tool":
                jd_text = json_args.get("jd_text", "")
                result = await analyze_job_description_api(jd_text)

                return ToolMessage(
                    tool_call_id=function_id,
                    status="success",
                    content=json.dumps(result.as_context()),
                )

            case "analyze_resume_tool":
                resume_text = json_args.get("resume_text", "")
                result = await review_resume_api(resume_text)

                return ToolMessage(
                    tool_call_id=function_id,
                    status="success",
                    content=json.dumps(result.as_context()),
                )

            case "analyze_candidate_fit_tool":
                resume_text = json_args.get("resume_text", "")
                jd_text = json_args.get("jd_text", "")
                result = await calculate_fit_score_api(resume_text, jd_text)

                return ToolMessage(
                    tool_call_id=function_id,
                    status="success",
                    content=json.dumps(result.as_context()),
                )

    except Exception as e:
        logger.error(
            f"Error in analysis_call_handler for {function_name}: {str(e)}",
            exc_info=True,
        )
        return ToolMessage(
            tool_call_id=function_id,
            status="error",
            content=f"Error: {str(e)}",
        )

    return ToolMessage(
        tool_call_id=function_id,
        status="error",
        content=f"No tool with name: {function_name}",
    )
