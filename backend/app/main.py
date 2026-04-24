from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, notes, search, rag


app = FastAPI(
    title="Karpathy Knowledge Base API",
    description="Obsidian + AI 驱动的个人知识库后端 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(rag.router, prefix="/api", tags=["rag"])


@app.get("/")
async def root():
    return {"message": "Karpathy Knowledge Base API", "version": "0.1.0"}
