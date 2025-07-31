import aiohttp
from utils.vars import get_news_api_key
from utils.constants import NEWS_API_URL
from job_analyzer.external_api.models import NewsResponse


async def fetch_news(url: str, params: dict[str, str]) -> dict:
    """Fetch Response with given URL and parameters"""

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()


async def get_recent_news(
    keyword: str, from_date: str, sort_by="popularity"
) -> NewsResponse:
    """Get Recent News with keyword, from date, and sortBy"""

    params = {
        "q": keyword,
        "from": from_date,
        "sortBy": sort_by.lower(),
        "apiKey": get_news_api_key(),
    }

    fetched_news = await fetch_news(NEWS_API_URL, params)

    return NewsResponse(**fetched_news)
