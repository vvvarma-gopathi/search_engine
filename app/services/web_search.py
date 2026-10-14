
import os
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv
from tavily import TavilyClient

from app.schemas.search import SearchResponse, SearchSource
from app.services.content_limiter import limit_content
from app.services.planner import generate_queries

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    raise RuntimeError("TAVILY_API_KEY is missing")

tavily = TavilyClient(api_key=api_key)

MAX_RESULTS = max(
    1,
    int(os.getenv("MAX_RESULTS_PER_QUERY", "5")),
)


def normalize_url(value: str) -> str | None:
    try:
        parts = urlsplit(value)

        if parts.scheme not in {"http", "https"}:
            return None

        if not parts.hostname:
            return None

        if parts.username or parts.password:
            return None

        return urlunsplit((
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path.rstrip("/") or "/",
            parts.query,
            "",
        ))
    except (ValueError, TypeError):
        return None


def search_web(user_query: str) -> SearchResponse:
    queries = generate_queries(user_query)
    collected = []
    answer = ""

    for index, query in enumerate(queries):
        response = tavily.search(
            query=query,
            search_depth="basic",
            topic="general",
            max_results=MAX_RESULTS,
            include_answer="basic" if index == 0 else False,
            include_raw_content="markdown",
        )

        if index == 0:
            answer = response.get("answer") or ""

        for result in response.get("results", []):
            original_url = result.get("url", "")
            normalized = normalize_url(original_url)

            if not normalized:
                continue

            collected.append({
                "title": result.get("title") or normalized,
                "url": original_url,
                "normalized_url": normalized,
                "content": result.get("content") or "",
                "raw_content": result.get("raw_content") or "",
                "published_date": (
                    result.get("published_date")
                    or result.get("published_time")
                ),
                "score": result.get("score") or 0,
            })

    unique_results = []
    seen_urls = set()

    for result in collected:
        url = result["normalized_url"]

        if url in seen_urls:
            continue

        seen_urls.add(url)
        unique_results.append(result)

    unique_results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    unique_results = limit_content(unique_results)

    sources = [
        SearchSource(
            title=item["title"],
            url=item["url"],
            snippet=item["content"][:1500],
            published_date=item["published_date"],
            extracted_content=item["raw_content"],
        )
        for item in unique_results
    ]

    if not answer:
        answer = (
            "The search provider did not return a generated answer. "
            "Review the source links below for relevant information."
        )

    return SearchResponse(
        query=user_query,
        answer=answer,
        sources=sources,
        search_queries=queries,
    )
