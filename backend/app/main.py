import atexit
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, notes, search, rag
from app.middleware.auth import APIKeyAuthMiddleware
from app.services.indexer import Indexer
from app.services.file_watcher import FileWatcher


_file_watcher: FileWatcher | None = None
_indexer: Indexer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _file_watcher, _indexer
    if settings.FILE_WATCHER_ENABLED:
        _indexer = Indexer()
        _file_watcher = FileWatcher(
            vault_path=settings.VAULT_PATH,
            mode=settings.FILE_WATCHER_MODE,
            poll_interval=settings.FILE_WATCHER_POLL_INTERVAL,
            debounce=settings.FILE_WATCHER_DEBOUNCE,
            on_change=_indexer.on_file_change,
        )
        # Initial full vault indexing
        _indexer.upsert_all_notes()
        _file_watcher.start()
        atexit.register(_file_watcher.stop)
    yield
    if _file_watcher:
        _file_watcher.stop()


app = FastAPI(
    title="Karpathy Knowledge Base API",
    description="Obsidian + AI 驱动的个人知识库后端 API",
    version="0.1.0",
    lifespan=lifespan,
)

origins_str = settings.BACKEND_CORS_ORIGINS
origins = [o.strip() for o in origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(APIKeyAuthMiddleware)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(rag.router, prefix="/api", tags=["rag"])


@app.get("/")
async def root():
    return {"message": "Karpathy Knowledge Base API", "version": "0.1.0"}
