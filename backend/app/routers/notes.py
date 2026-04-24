from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import Note, NoteListResponse, NoteWithBacklinks, BacklinkItem
from app.services.vault_reader import VaultReader, get_vault_reader
from app.services.backlinks import BacklinksService, get_backlinks

router = APIRouter()


@router.get("/notes", response_model=NoteListResponse)
async def list_notes(
    reader: VaultReader = Depends(get_vault_reader),
    search: str | None = Query(default=None, description="Search in title and content"),
):
    notes = reader.list_notes(search=search)
    return NoteListResponse(notes=[Note(**n) for n in notes], total=len(notes))


@router.get("/notes/{note_id}", response_model=NoteWithBacklinks)
async def get_note(
    note_id: str,
    reader: VaultReader = Depends(get_vault_reader),
    backlinks_service: BacklinksService = Depends(get_backlinks),
):
    note = reader.get_note_by_id(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    raw_backlinks = backlinks_service.get_backlinks_with_context(note_id)

    note_with_backlinks = NoteWithBacklinks(
        **note,
        backlinks=[BacklinkItem(**bl) for bl in raw_backlinks],
    )
    return note_with_backlinks


@router.get("/notes/{note_id}/backlinks", response_model=list[BacklinkItem])
async def get_note_backlinks(
    note_id: str,
    reader: VaultReader = Depends(get_vault_reader),
    backlinks_service: BacklinksService = Depends(get_backlinks),
):
    """返回引用了指定笔记的所有来源笔记及其引用片段。"""
    note = reader.get_note_by_id(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    raw_backlinks = backlinks_service.get_backlinks_with_context(note_id)
    return [BacklinkItem(**bl) for bl in raw_backlinks]
