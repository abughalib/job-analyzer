"""LLM-based analysis API for job descriptions and resumes."""

import json
import logging
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from llm.inference import Inference
from job_analyzer.external_api.models import (
    JobDescriptionAnalysis,
    ResumeReview,
    FitScore,
)

logger = logging.getLogger(__name__)


async def _call_llm_for_analysis(prompt: str) -> str:
    """
    Helper function to call the LLM for analysis tasks.

    Args:
        prompt: The structured prompt for the LLM.

    Returns:
        str: The LLM's response.

    Raises:
        RuntimeError: If the LLM call fails.
    """
    try:
        inference = Inference()
        messages = [
            SystemMessage(
                content="You are a helpful assistant that provides structured JSON responses."
            ),
            HumanMessage(content=prompt),
        ]
        logger.debug(f"Sending request to LLM. Prompt length: {len(prompt)}")
        response = await inference.chat(messages)
        logger.debug(
            f"Received response from LLM (first 200 chars): {response[:200]}..."
        )
        return response
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"LLM call failed: {str(e)}")


def _extract_json_from_response(response: str) -> Optional[dict]:
    """
    Extract JSON object from LLM response.

    Args:
        response: The LLM response string.

    Returns:
        Optional[dict]: Parsed JSON dict or None if extraction fails.
    """
    try:
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        if start_idx != -1 and end_idx != -1:
            json_str = response[start_idx : end_idx + 1]
            return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {str(e)}", exc_info=True)
    return None


async def analyze_job_description_api(jd_text: str) -> JobDescriptionAnalysis:
    """
    Analyze a job description to extract key information using LLM.

    Args:
        jd_text: The full text of the job description.

    Returns:
        JobDescriptionAnalysis: Structured analysis of the job description.
    """
    prompt = """
You are the Job Description Standardization Engine. Your job is to convert unstructured job descriptions into a strictly controlled JSON schema. You never infer or assume requirements unless explicitly stated in the JD text.

OBJECTIVE
Parse the Job Description and output a normalized requirements dataset, including must-haves, nice-to-haves, deal-breakers, education, experience, and skills.

INPUT DATA
<job_description>
{jd_text}
</job_description>

RULES
1. Evidence-Based Only:
   - Extract only what is stated in the JD.
   - No assumptions, no expanding abbreviations unless explicitly defined.

2. Requirement Classification:
   - MUST-HAVE = phrases like “must”, “required”, “mandatory”, “need to”, “minimum”.
   - NICE-TO-HAVE = phrases like “preferred”, “nice to have”, “bonus”, “a plus”.
   - Deal-Breaker = mandatory items whose absence disqualifies a candidate (e.g., specific certifications, clearances, licenses). These must be explicitly stated.

3. Skill Taxonomy:
   - technical_skills: tools, programming languages, software, platforms, frameworks.
   - soft_skills: communication, leadership, teamwork, problem-solving.
   - Do not infer skills not stated.

4. Experience Extraction:
   - Capture seniority terms (e.g., “senior-level”, “junior”).
   - Capture explicit durations (e.g., “5+ years experience”).

5. Output Consistency:
   - All arrays must exist. If empty, return [].
   - No markdown formatting.

OUTPUT SCHEMA
{
  "role_title": "String",
  "must_have_requirements": ["Array of strings"],
  "nice_to_have_requirements": ["Array of strings"],
  "deal_breakers": ["Array of strings"],
  "technical_skills": ["Array of strings"],
  "soft_skills": ["Array of strings"],
  "experience_requirements": "String or null",
  "education_requirements": "String or null",
  "certification_requirements": ["Array of strings"],
  "industry_domain": "String or null",
  "additional_notes": "String or null"
}

RESPONSE
Return ONLY the raw JSON object.
"""

    try:
        logger.debug("Calling LLM for job description analysis")
        response = await _call_llm_for_analysis(prompt.format(jd_text=jd_text))
        result = _extract_json_from_response(response)

        if result:
            return JobDescriptionAnalysis(**result)
        else:
            logger.warning("Failed to parse JSON from LLM response")
            return JobDescriptionAnalysis(
                role_title="Could not extract",
            )
    except Exception as e:
        logger.error(f"Error during job description analysis: {str(e)}", exc_info=True)
        return JobDescriptionAnalysis(
            role_title="Error during extraction",
        )


async def review_resume_api(resume_text: str) -> ResumeReview:
    """
    Evaluate a resume against a job description using LLM.

    Args:
        resume_text: The full text of the resume.
        jd_text: The full text of the job description.

    Returns:
        ResumeReview: Structured review with strengths, gaps, and suggestions.
    """
    prompt = """
You are the Resume Evidence Extraction Engine. You do not evaluate, judge, compare, or score. You extract evidence ONLY from the resume text and represent it in a normalized JSON structure aligned with the Job Description Parser.

OBJECTIVE
Convert the resume into structured data identifying all explicit skills, experience, education, and achievements. Only extract information explicitly present in the resume text.

INPUT DATA
<candidate_resume>
{resume_text}
</candidate_resume>

RULES
1. Zero Inference:
   - Extract only what is explicitly written.
   - Do not infer skills from job titles (e.g., “Frontend Developer” ≠ React).

2. Skill Identification:
   - technical_skills = tools, languages, platforms, software explicitly listed.
   - soft_skills = explicit behavioral skills mentioned in text.

3. Experience Extraction:
   - Extract durations ONLY if stated (e.g., “3 years”, “2019-2023”).
   - Extract job titles, company names, and responsibilities.

4. Education:
   - Capture degrees, institutions, years, and GPA if present.

5. Certifications:
   - List certifications exactly as written.

6. No Judgement:
   - Do not categorize anything as a "match" or "gap".
   - Do not score or conclude.

OUTPUT SCHEMA
{
  "candidate_name": "String or null",
  "work_experience": [
    {
      "job_title": "String",
      "company": "String or null",
      "duration": "String or null",
      "responsibilities": "String or null"
    }
  ],
  "technical_skills": ["Array of Strings"],
  "soft_skills": ["Array of Strings"],
  "education": [
    {
      "degree": "String",
      "institution": "String or null",
      "year": "String or null"
    }
  ],
  "certifications": ["Array of Strings"],
  "projects": ["Array of Strings"],
  "achievements": ["Array of Strings"],
  "additional_info": "String or null"
}

RESPONSE
Return ONLY the raw JSON object.
"""

    try:
        logger.debug("Calling LLM for resume review")
        response = await _call_llm_for_analysis(prompt.format(resume_text=resume_text))
        result = _extract_json_from_response(response)

        if result:
            return ResumeReview(**result)
        else:
            logger.warning("Failed to parse JSON from LLM response")
            return ResumeReview()
    except Exception as e:
        logger.error(f"Error during resume review: {str(e)}", exc_info=True)
        return ResumeReview()


async def calculate_fit_score_api(resume_text: str, jd_text: str) -> FitScore:
    """
    Calculate a fit score for a candidate based on resume and JD using LLM.

    Args:
        resume_text: The full text of the resume.
        jd_text: The full text of the job description.

    Returns:
        FitScore: Score (0-100), confidence level, and explanation.
    """
    prompt = """
You are the Candidate Fit Scoring Engine. You compute a deterministic, weighted candidate–role fit score using structured JD data (Agent 1) and structured Resume data (Agent 2). You never infer or assume. You use only the evidence available.

OBJECTIVE
Compare parsed JD requirements with extracted resume evidence and apply the weighted scoring system to output a final hiring fit score.

INPUT DATA
<jd_parsed>
{jd_text}
</jd_parsed>

<resume_parsed>
{resume_text}
</resume_parsed>

SCORING POLICY (Strict)
1. HARD SKILLS (40%)
   - Compare JD.technical_skills vs Resume.technical_skills.
   - Award points proportionally to matches.
   - Missing MUST-HAVE technical skills reduce score heavily.

2. EXPERIENCE ALIGNMENT (30%)
   - Match required years of experience (if present).
   - Match seniority (e.g., senior, lead, junior).
   - Match industry domain when explicitly stated.

3. EDUCATION & CERTIFICATIONS (10%)
   - Award proportional points if resume matches required degrees or certifications.

4. SOFT SKILLS & CULTURE (20%)
   - Award points only for explicit soft skills in resume that appear in JD.

CRITICAL OVERRIDE
If any JD "deal_breaker" requirement is missing from the resume:
- overall_score = 0
- List missing deal breakers in deal_breakers_found

ADDITIONAL RULES
- Zero inference: if a skill or qualification is not explicitly in the resume, it is considered missing.
- Use only data from parsed JSON; ignore raw text.
- Always compute partial points; don't round until the final total.
- No markdown formatting.

OUTPUT SCHEMA
{
  "overall_score": "Integer (0-100)",
  "score_breakdown": {
    "hard_skills": "Integer (0-40)",
    "experience": "Integer (0-30)",
    "education": "Integer (0-10)",
    "soft_skills": "Integer (0-20)"
  },
  "deal_breakers_found": ["Array of strings"],
  "reasoning_trace": "Concise list of deductions and matches driving the scoring.",
  "final_recommendation": "Strong Fit | Potential Fit | Weak Fit | No Fit",
  "data_sufficiency": "High | Medium | Low"
}

RESPONSE
Return ONLY the raw JSON object.
"""

    try:
        logger.debug("Calling LLM for fit score calculation")
        response = await _call_llm_for_analysis(
            prompt.format(jd_text=jd_text, resume_text=resume_text)
        )
        result = _extract_json_from_response(response)

        if result:
            return FitScore(**result)
        else:
            logger.warning("Failed to parse JSON from LLM response")
            from job_analyzer.external_api.models import ScoreBreakdown

            return FitScore(
                overall_score=0,
                score_breakdown=ScoreBreakdown(
                    hard_skills=0, experience=0, education=0, soft_skills=0
                ),
                deal_breakers_found=[],
                reasoning_trace="Could not calculate score",
                final_recommendation="No Fit",
                data_sufficiency="Low",
            )
    except Exception as e:
        logger.error(f"Error during fit score calculation: {str(e)}", exc_info=True)
        from job_analyzer.external_api.models import ScoreBreakdown

        return FitScore(
            overall_score=0,
            score_breakdown=ScoreBreakdown(
                hard_skills=0, experience=0, education=0, soft_skills=0
            ),
            deal_breakers_found=[],
            reasoning_trace="Error during scoring",
            final_recommendation="No Fit",
            data_sufficiency="Low",
        )
