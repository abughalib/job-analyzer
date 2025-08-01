import aiohttp
from utils.constants import LANGSEARCH_URL
from utils.vars import get_langsearch_api_key
from job_analyzer.external_api.models import LangSearchResult


async def fetch_langsearch(
    url: str, header: dict[str, str], body: dict[str, str]
) -> dict:
    """Fetch Response with given URL and parameters"""

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=header, json=body) as response:
            return await response.json()


async def get_langsearch(keyword: str, limit: int) -> LangSearchResult:
    """Get LangSearch Result with keyword"""

    headers = {"Authorization": f"Bearer {get_langsearch_api_key()}", "Content-Type": "application/json"}
    body = {"query": keyword, "freshness": "onLimit", "count": limit}

    fetched_langsearch = await fetch_langsearch(LANGSEARCH_URL, headers, body)

    return LangSearchResult(**fetched_langsearch)
