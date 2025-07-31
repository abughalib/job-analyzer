import json
from typing import Optional

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
