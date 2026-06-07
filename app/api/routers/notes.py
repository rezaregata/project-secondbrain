from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_note_service
from app.services.note_service import NoteService

router = APIRouter()


class NoteCreate(BaseModel):
    content: str


class NoteResponse(BaseModel):
    id: int
    title: str | None
    content: str
    category: str | None
    tags: list[str] | None
    
    class Config:
        from_attributes = True


@router.post("/", response_model=NoteResponse)
def create_note(
    note_in: NoteCreate,
    note_service: NoteService = Depends(get_note_service),
):
    note = note_service.save_note(content=note_in.content)
    return note


@router.get("/", response_model=list[NoteResponse])
def get_all_notes(
    note_service: NoteService = Depends(get_note_service),
):
    notes = note_service.get_all_notes()
    return notes


@router.get("/recent", response_model=list[NoteResponse])
def get_recent_notes(
    days: int = 7,
    note_service: NoteService = Depends(get_note_service),
):
    notes = note_service.get_recent_notes(days=days)
    return notes


@router.get("/tags", response_model=list[str])
def get_all_tags(
    note_service: NoteService = Depends(get_note_service),
):
    return note_service.get_all_tags()


@router.get("/tag/{tag_name}", response_model=list[NoteResponse])
def get_notes_by_tag(
    tag_name: str,
    note_service: NoteService = Depends(get_note_service),
):
    notes = note_service.get_notes_by_tag(tag_name)
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
def get_note_by_id(
    note_id: int,
    note_service: NoteService = Depends(get_note_service),
):
    from fastapi import HTTPException
    note = note_service.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
