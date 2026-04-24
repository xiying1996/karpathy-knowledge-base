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


class BacklinkItem(BaseModel):
    """引用了某笔记的来源笔记信息"""
    id: str
    title: str
    snippet: str = ""


class NoteWithBacklinks(Note):
    """笔记详情（含反向链接）"""
    backlinks: list[BacklinkItem] = []
