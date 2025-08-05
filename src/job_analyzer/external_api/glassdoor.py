import aiohttp
from typing import Optional
from utils.vars import get_rapid_api_key
from job_analyzer.external_api.models import (
    GlassDoorSalaryResponse,
    GlassdoorLocation,
)
from utils.constants import (
    GLASSDOOR_API_URL,
    GLASSDOOR_HOST,
    GLASSDOOR_LOCATION_API_URL,
    GLASSDOOR_YEARS_OF_EXPERINCE,
    GLASSDOOR_SORT_OPTIONS,
)


async def fetch_location_data(
    url: str, headers: dict[str, str], params: dict[str, str]
) -> dict:
    """
    Asynchronously fetches location data from the Glassdoor API.
    """

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Error fetching location data: {e}")


async def fetch_salary_data(
    url: str, headers: dict[str, str], params: dict[str, str]
) -> dict:
    """
    Asynchronously fetches salary data from the Glassdoor API.
    """

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Error fetching salary data: {e}")


async def get_salary_data(
    company_name: str,
    location: Optional[str] = None,
    job_function: Optional[str] = None,
    year_of_experience: Optional[str] = None,
    limit: int = 10,
    page=1,
    sort: str = "POPULAR",
):

    headers = {
        "x-rapidapi-host": GLASSDOOR_HOST,
        "x-rapidapi-key": get_rapid_api_key(),
    }

    if location:
        location_data_raw = await fetch_location_data(
            GLASSDOOR_LOCATION_API_URL, headers, {"query": location}
        )
        location_data = GlassdoorLocation(**location_data_raw)
        headers["locationId"] = location_data.data[0].locationId

    if job_function:
        headers["jobFunction"] = job_function

    if year_of_experience and year_of_experience in GLASSDOOR_YEARS_OF_EXPERINCE:
        headers["yearOfExperience"] = str(year_of_experience)

    if sort and sort in GLASSDOOR_SORT_OPTIONS:
        headers["sort"] = sort

    headers["limit"] = str(limit)
    headers["page"] = str(page)
    headers["sort"] = sort

    params = {"query": company_name}

    salary_data = await fetch_salary_data(GLASSDOOR_API_URL, headers, params)

    return GlassDoorSalaryResponse(**salary_data)
