import json
from typing import Optional, Any

from pydantic import (
    BaseModel,
    HttpUrl,
    Field,
    field_validator,
)


class Source(BaseModel):
    id: Optional[str]
    name: str


class Article(BaseModel):
    source: Source
    author: Optional[str]
    title: str
    description: Optional[str]
    url: HttpUrl
    urlToImage: Optional[HttpUrl]
    publishedAt: str
    content: Optional[str]

    @field_validator("urlToImage", mode="before")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class NewsResponse(BaseModel):
    status: str
    totalResults: int
    articles: list[Article]

    def as_context(self, limit: int = 5) -> dict[str, str]:

        return {
            "status": self.status,
            "articles": json.dumps(
                [article.model_dump(mode="json") for article in self.articles[:limit]]
            ),
        }


class LangSearchArticle(BaseModel):
    id: str
    name: str
    url: HttpUrl
    displayUrl: HttpUrl
    snippet: str
    summary: str
    datePublished: Optional[str]
    dateLastCrawled: Optional[str]

    def as_context(self) -> dict[str, str]:

        return {"heading": self.snippet, "summary": self.summary}


class WebPages(BaseModel):
    webSearchUrl: str
    totalEstimatedMatches: Optional[int]
    value: list[LangSearchArticle]
    someResultsRemoved: Optional[bool]


class LangSearchData(BaseModel):
    _type: str
    queryContext: dict[str, str]
    webPages: Optional[WebPages]


class LangSearchResult(BaseModel):
    code: int
    log_id: str
    msg: Optional[str]
    data: Optional[LangSearchData]

    def as_context(self, limit: int) -> dict[str, Any]:

        if self.data is None or self.data.webPages is None:
            return {}

        return {
            "articles": json.dumps(
                [article.as_context() for article in self.data.webPages.value[:limit]]
            )
        }


class QueryItem(BaseModel):
    title: Optional[str]
    totalResults: Optional[str]
    searchTerms: Optional[str]
    count: Optional[int]
    startIndex: Optional[int]
    inputEncoding: Optional[str]
    outputEncoding: Optional[str]
    safe: Optional[str]
    cx: Optional[str]


class Queries(BaseModel):
    request: list[QueryItem]
    nextPage: list[QueryItem]


class SearchItems(BaseModel):
    kind: str
    title: str
    htmlTitle: str
    link: str
    displayLink: str
    snippet: str
    htmlSnippet: str
    formattedUrl: str
    htmlFormattedUrl: str
    pagemap: Optional[dict[str, list[dict[str, str]]]]


class SearchInformation(BaseModel):
    searchTime: float
    formattedSearchTime: str
    totalResults: str
    formattedTotalResults: str


class GoogleSearchResult(BaseModel):
    kind: str
    url: dict[str, str]
    queries: Queries
    context: dict[str, str]
    searchInformation: SearchInformation
    items: list[SearchItems]

    def as_context(self, limit: int) -> dict[str, Any]:

        return {
            "results": [
                {"heading": result.snippet, "url": result.formattedUrl}
                for result in self.items[:limit]
            ]
        }


# --- AggregateSalaryResponse Nested Models ---


class PayStatistics(BaseModel):
    """Represents basic pay statistics with a mean value."""

    mean: Optional[float] = None


class Currency(BaseModel):
    """Represents a currency with its code and ID."""

    code: Optional[str] = None
    id: Optional[int] = None


class GlobalJobCount(BaseModel):
    """Represents the global job count for an employer."""

    job_count: Optional[int] = Field(None, alias="jobCount")


class Counts(BaseModel):
    """Container for various counts related to an employer."""

    global_job_count: Optional[GlobalJobCount] = Field(None, alias="globalJobCount")


class Ratings(BaseModel):
    """Represents employer ratings."""

    overall_rating: Optional[float] = Field(None, alias="overallRating")


class Employer(BaseModel):
    """Represents an employer with its details and ratings."""

    counts: Optional[Counts] = None
    id: Optional[int] = None
    name: Optional[str] = None
    ratings: Optional[Ratings] = None
    short_name: Optional[str] = Field(None, alias="shortName")
    square_logo_url: Optional[str] = Field(None, alias="squareLogoUrl")


class JobTitle(BaseModel):
    """Represents a job title with its identifiers."""

    goc_id: Optional[int] = Field(None, alias="gocId")
    id: Optional[int] = None
    text: Optional[str] = None


class Percentile(BaseModel):
    """Represents a specific percentile value."""

    ident: Optional[str] = None
    value: Optional[float] = None


class TotalPayStatistics(BaseModel):
    """Represents total pay statistics including percentiles."""

    typename: Optional[str] = Field(None, alias="__typename")
    percentiles: Optional[list[Percentile]] = None


class GlassDoorResultItem(BaseModel):
    """Represents a single salary result item in the aggregate response."""

    base_pay_statistics: Optional[PayStatistics] = Field(
        None, alias="basePayStatistics"
    )
    currency: Optional[Currency] = None
    employer: Optional[Employer] = None
    job_title: Optional[JobTitle] = Field(None, alias="jobTitle")
    pay_period: Optional[str] = Field(None, alias="payPeriod")
    total_additional_pay_statistics: Optional[PayStatistics] = Field(
        None, alias="totalAdditionalPayStatistics"
    )
    total_pay_statistics: Optional[TotalPayStatistics] = Field(
        None, alias="totalPayStatistics"
    )


class AggregateQueryLocation(BaseModel):
    """Represents the location used in the aggregate salary query."""

    id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None


class AggregateSalaryResponse(BaseModel):
    """Represents the main aggregate salary response from the API."""

    num_pages: Optional[int] = Field(None, alias="numPages")
    query_location: Optional[AggregateQueryLocation] = Field(
        None, alias="queryLocation"
    )
    result_count: Optional[int] = Field(None, alias="resultCount")
    results: Optional[list[GlassDoorResultItem]] = None


# --- OccSalaryResponse Nested Models ---


class OccPercentile(BaseModel):
    """Represents a percentile value in the occupational salary response."""

    percentile: Optional[str] = None
    value: Optional[float] = None


class OccQueryLocation(BaseModel):
    """Represents the location used in the occupational salary query."""

    name: Optional[str] = None


class LashedJobTitle(BaseModel):
    """Represents a simple job title with ID and text."""

    id: Optional[int] = None
    text: Optional[str] = None


class OccSalaryResponse(BaseModel):
    """Represents the occupational salary response from the API."""

    additional_pay_percentiles: Optional[list[OccPercentile]] = Field(
        None, alias="additionalPayPercentiles"
    )
    base_pay_percentiles: Optional[list[OccPercentile]] = Field(
        None, alias="basePayPercentiles"
    )
    confidence: Optional[str] = None
    currency: Optional[Currency] = None
    employers_count: Optional[int] = Field(None, alias="employersCount")  # Can be null
    estimate_source_name: Optional[str] = Field(None, alias="estimateSourceName")
    estimate_source_update_time: Optional[str] = Field(
        None, alias="estimateSourceUpdateTime"
    )
    estimate_source_version: Optional[str] = Field(None, alias="estimateSourceVersion")
    job_title: Optional[LashedJobTitle] = Field(None, alias="jobTitle")
    pay_period: Optional[str] = Field(None, alias="payPeriod")
    query_location: Optional[OccQueryLocation] = Field(None, alias="queryLocation")
    salaries_count: Optional[int] = Field(None, alias="salariesCount")
    total_pay_percentiles: Optional[list[OccPercentile]] = Field(
        None, alias="totalPayPercentiles"
    )


# --- Top-Level Models ---


class GlassDoorDataObject(BaseModel):
    """The main 'data' object containing all salary responses."""

    aggregate_salary_response: Optional[AggregateSalaryResponse] = Field(
        None, alias="aggregateSalaryResponse"
    )
    lashed_job_title: Optional[LashedJobTitle] = Field(None, alias="lashedJobTitle")
    occ_salary_response: Optional[OccSalaryResponse] = Field(
        None, alias="occSalaryResponse"
    )


class GlassDoorMeta(BaseModel):
    """Metadata for pagination."""

    current_page: Optional[int] = Field(None, alias="currentPage")
    limit: Optional[int] = None
    total_records: Optional[int] = Field(None, alias="totalRecords")
    total_page: Optional[int] = Field(None, alias="totalPage")


class GlassDoorSalaryResponse(BaseModel):
    """The root model for the entire API response."""

    data: Optional[GlassDoorDataObject] = None
    meta: Optional[GlassDoorMeta] = None
    status: Optional[bool] = None
    message: Optional[str] = None

    def as_context(self) -> dict[str, Any]:

        query_location = ""

        if (
            (not self.data)
            or (not self.data.aggregate_salary_response)
            or (not self.data.aggregate_salary_response.results)
        ):
            return {}

        salary_result = []
        if (
            self.data.aggregate_salary_response
            and self.data.aggregate_salary_response.query_location
            and self.data.aggregate_salary_response.query_location.name
        ):
            query_location = self.data.aggregate_salary_response.query_location.name
            salary_result = self.data.aggregate_salary_response.results

        return {
            "location": query_location,
            "salaries": json.dumps(
                [
                    {
                        "currency": salary.currency.code if salary.currency else "",
                        "title": salary.job_title.text if salary.job_title else "",
                        "mean_salary": (
                            salary.base_pay_statistics.mean
                            if salary.base_pay_statistics
                            else ""
                        ),
                        "salary_percentile": (
                            json.dumps(
                                [
                                    {
                                        "ident": percentile.ident,
                                        "value": percentile.value,
                                    }
                                    for percentile in salary.total_pay_statistics.percentiles
                                ]
                            )
                            if salary.total_pay_statistics
                            and salary.total_pay_statistics.percentiles
                            else ""
                        ),
                    }
                    for salary in salary_result
                ]
            ),
        }


# --- Glassdoor Location ---- #


class GlassdoorLocationData(BaseModel):
    countryId: int
    locationId: str
    locationName: str
    locationType: str


class GlassdoorLocation(BaseModel):
    data: list[GlassdoorLocationData]
    status: bool
    message: str
