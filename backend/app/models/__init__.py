from pydantic import BaseModel


class Note(BaseModel):
    id: str
    title: str
    content: str
    path: str
    tags: list[str] = []
    links: list[str] = []
    created: str | None = None
    modified: str | None = None


class NoteListResponse(BaseModel):
    notes: list[Note]
    total: int


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class SearchResult(BaseModel):
    id: str
    title: str
    snippet: str
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str


class AskRequest(BaseModel):
    question: str
    context_limit: int = 5


class AskResponse(BaseModel):
    answer: str
    sources: list[str] = []
