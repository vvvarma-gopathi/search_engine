
from pydantic import BaseModel, Field, HttpUrl


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)


class SearchSource(BaseModel):
    title: str
    url: HttpUrl
    snippet: str = ""
    published_date: str | None = None
    extracted_content: str = ""


class SearchResponse(BaseModel):
    query: str
    answer: str
    sources: list[SearchSource]
    search_queries: list[str]
