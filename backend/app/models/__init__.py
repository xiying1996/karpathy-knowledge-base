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


# ─── Daily Note 模型 ─────────────────────────────────────────────────────────


class DailyNoteCreateRequest(BaseModel):
    """创建每日笔记请求"""
    date: str | None = None  # YYYY-MM-DD，默认今天
    force: bool = False  # 是否覆盖已有
    use_ai_suggestion: bool = False  # 是否使用 AI 建议主题


class DailyNoteCreateResponse(BaseModel):
    """创建每日笔记响应"""
    success: bool
    note_id: str
    path: str
    created: bool  # true=新建, false=已存在
    content_preview: str


class DailyTemplateResponse(BaseModel):
    """模板响应"""
    template: str
    is_custom: bool  # 是否用户自定义


class DailyTemplateUpdateRequest(BaseModel):
    """更新模板请求"""
    template: str


class DailyNoteListItem(BaseModel):
    """每日笔记列表项"""
    id: str
    title: str
    created: str


class DailyNoteListResponse(BaseModel):
    """每日笔记列表响应"""
    notes: list[DailyNoteListItem]


class DailyStreakResponse(BaseModel):
    """连续记录统计"""
    current_streak: int
    longest_streak: int
    total_days: int
