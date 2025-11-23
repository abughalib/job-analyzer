"""Document summarization utility to manage LLM context limits."""

import logging
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from llm.inference import Inference

logger = logging.getLogger(__name__)

# Token limits (conservative estimates)
MAX_TOKENS_PER_DOCUMENT = 4000  # Leave room for other context
CHARS_PER_TOKEN = 4  # Rough estimate
MAX_CHARS = MAX_TOKENS_PER_DOCUMENT * CHARS_PER_TOKEN


async def summarize_document(
    text: str,
    doc_type: str = "document",
    max_length: int = MAX_CHARS,
) -> str:
    """
    Summarize a document if it exceeds the maximum length.

    Args:
        text: The full document text.
        doc_type: Type of document (resume, job_description, etc.)
        max_length: Maximum character length before summarization.

    Returns:
        Original text if under limit, otherwise summarized version.
    """
    if len(text) <= max_length:
        logger.debug(
            f"Document size ({len(text)} chars) within limit, no summarization needed"
        )
        return text

    logger.info(
        f"Document size ({len(text)} chars) exceeds limit ({max_length}), summarizing..."
    )

    try:
        summary = await _generate_summary(text, doc_type)
        logger.info(f"Summarized from {len(text)} to {len(summary)} characters")
        return summary
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        # Fallback: truncate with warning
        truncated = text[:max_length]
        logger.warning(f"Falling back to truncation at {max_length} chars")
        return f"[TRUNCATED DUE TO LENGTH]\n\n{truncated}\n\n[...Content truncated...]"


async def _generate_summary(text: str, doc_type: str) -> str:
    """
    Generate a summary using LLM.

    Args:
        text: The full document text.
        doc_type: Type of document for context-aware summarization.

    Returns:
        Summarized text.
    """
    prompts = {
        "resume": """Summarize this resume, preserving ALL key information:
- Work experience (companies, roles, durations, key achievements)
- Skills (technical and soft)
- Education (degrees, institutions)
- Certifications
- Projects and achievements

Keep the summary comprehensive but concise. Do not lose critical details.""",
        "job_description": """Summarize this job description, preserving ALL requirements:
- Role title and level
- Required skills and experience
- Must-have vs nice-to-have requirements
- Deal-breakers and mandatory qualifications
- Education and certification requirements

Be thorough - include all specific requirements.""",
        "document": """Summarize this document comprehensively, preserving all key information and important details.""",
    }

    prompt_template = prompts.get(doc_type, prompts["document"])

    prompt = f"""{prompt_template}

<document>
{text}
</document>

Provide a clear, structured summary that retains all important information."""

    try:
        inference = Inference()
        messages = [
            SystemMessage(
                content="You are a document summarization expert. Preserve all critical information."
            ),
            HumanMessage(content=prompt),
        ]
        summary = await inference.chat(messages)
        return summary.strip()
    except Exception as e:
        logger.error(f"LLM summarization failed: {str(e)}", exc_info=True)
        raise


async def prepare_document_for_analysis(
    text: str,
    doc_type: str = "document",
) -> str:
    """
    Prepare a document for LLM analysis by summarizing if necessary.

    This is a convenience function that wraps summarize_document with
    context-specific settings.

    Args:
        text: The full document text.
        doc_type: Type of document (resume, job_description, etc.)

    Returns:
        Document text ready for LLM processing (original or summarized).
    """
    return await summarize_document(text, doc_type=doc_type)
