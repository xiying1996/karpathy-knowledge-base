from fastapi import APIRouter
from app.models import SearchRequest, SearchResponse

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_notes(request: SearchRequest):
    return SearchResponse(results=[], query=request.query)
