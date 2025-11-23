"""Unit tests for LLM-based analysis tools."""

import pytest
from job_analyzer.external_api.llm_analysis import (
    analyze_job_description_api,
    review_resume_api,
    calculate_fit_score_api,
)


@pytest.mark.asyncio
async def test_analyze_job_description():
    """Test job description analysis extracts structured data."""
    jd_text = (
        "We are looking for a Senior Python Developer with 5+ years of experience."
    )
    result = await analyze_job_description_api(jd_text)
    assert result.role_title
    assert isinstance(result.technical_skills, list)
    assert isinstance(result.must_have_requirements, list)


@pytest.mark.asyncio
async def test_review_resume():
    """Test resume extraction from text."""
    resume_text = "Experienced Python Developer with 5 years of experience in backend development."
    result = await review_resume_api(resume_text)
    assert isinstance(result.work_experience, list)
    assert isinstance(result.technical_skills, list)
    assert isinstance(result.soft_skills, list)


@pytest.mark.asyncio
async def test_calculate_fit_score():
    """Test fit score calculation."""
    resume_text = "Experienced Python Developer with 5 years of experience."
    jd_text = "Senior Python Developer with 5+ years required."
    result = await calculate_fit_score_api(resume_text, jd_text)
    assert 0 <= result.overall_score <= 100
    assert result.final_recommendation in [
        "Strong Fit",
        "Potential Fit",
        "Weak Fit",
        "No Fit",
    ]
    assert result.data_sufficiency in ["High", "Medium", "Low"]
    assert isinstance(result.score_breakdown.hard_skills, int)
