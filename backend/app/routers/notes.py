from fastapi import APIRouter, HTTPException
from app.models import Note, NoteListResponse

router = APIRouter()


@router.get("/notes", response_model=NoteListResponse)
async def list_notes():
    return NoteListResponse(notes=[], total=0)


@router.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: str):
    raise HTTPException(status_code=404, detail="Note not found")
