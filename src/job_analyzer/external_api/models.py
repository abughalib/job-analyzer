import json
from typing import Optional, Any

from pydantic import BaseModel, HttpUrl, field_validator


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
