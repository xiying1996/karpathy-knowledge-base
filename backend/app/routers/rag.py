from fastapi import APIRouter

from app.models import AskRequest, AskResponse
from app.services.rag_engine import get_rag_engine

router = APIRouter()


@router.post("/rag/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    """
    RAG 问答：基于知识库的语义检索 + LLM 生成。
    """
    rag = get_rag_engine()
    answer, sources = rag.ask(request.question, context_limit=request.context_limit)
    return AskResponse(answer=answer, sources=sources)
