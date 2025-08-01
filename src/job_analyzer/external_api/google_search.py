import aiohttp
from utils.vars import get_google_search_api_key
from job_analyzer.external_api.models import GoogleSearchResult
from utils.constants import GOOGLE_SEARCH_URL, GOOGLE_SERACH_CX


async def fetch_google_search(url: str, params: dict[str, str]) -> dict:
    """Fetch Response with given URL and parameters"""

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()


async def get_google_search_result(keyword: str) -> GoogleSearchResult:
    """Get Google Search Result with keyword"""

    params = {"key": get_google_search_api_key(), "cx": GOOGLE_SERACH_CX, "q": keyword}

    fetched_google_search = await fetch_google_search(GOOGLE_SEARCH_URL, params)

    return GoogleSearchResult(**fetched_google_search)
