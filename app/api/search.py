
import logging

from fastapi import APIRouter, HTTPException

from app.schemas.search import SearchRequest, SearchResponse
from app.services.web_search import search_web

router = APIRouter(prefix="/api/v1", tags=["search"])
logger = logging.getLogger(__name__)


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    query = " ".join(request.query.split())

    try:
        return search_web(query)
    except Exception as exc:
        logger.exception("Search failed for query: %s", query)

        raise HTTPException(
            status_code=502,
            detail=f"Search failed: {type(exc).__name__}. Check backend logs.",
        ) from exc
