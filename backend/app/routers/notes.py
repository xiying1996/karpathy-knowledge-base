from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.models import Note, NoteListResponse
from app.services.vault_reader import VaultReader

router = APIRouter()

_vault_reader: VaultReader | None = None


def get_vault_reader() -> VaultReader:
    global _vault_reader
    if _vault_reader is None:
        _vault_reader = VaultReader(settings.VAULT_PATH)
    return _vault_reader


@router.get("/notes", response_model=NoteListResponse)
async def list_notes(search: str | None = Query(default=None, description="Search in title and content")):
    reader = get_vault_reader()
    notes = reader.list_notes(search=search)
    return NoteListResponse(notes=[Note(**n) for n in notes], total=len(notes))


@router.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: str):
    reader = get_vault_reader()
    note = reader.get_note_by_id(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return Note(**note)