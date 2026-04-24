from fastapi import APIRouter

from app.models import SearchRequest, SearchResponse, SearchResult
from app.services.vector_store import get_vector_store

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_notes(request: SearchRequest):
    vs = get_vector_store()
    results = vs.query(query_texts=[request.query], n_results=request.limit)
    search_results = [
        SearchResult(
            id=r["note_id"],
            title=r["title"],
            snippet=r["snippet"],
            score=r["score"],
        )
        for r in results
    ]
    return SearchResponse(results=search_results, query=request.query)
