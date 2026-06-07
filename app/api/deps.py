from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database.connection import get_session
from app.services.ai_service import AIService
from app.services.embedding_service import EmbeddingService
from app.services.note_service import NoteService


def get_ai_service(settings: Settings = Depends(get_settings)) -> AIService:
    return AIService(settings)


def get_embedding_service(settings: Settings = Depends(get_settings)) -> EmbeddingService:
    return EmbeddingService(settings)


def get_note_service(
    session: Session = Depends(get_session),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    ai_service: AIService = Depends(get_ai_service),
) -> NoteService:
    return NoteService(session, embedding_service, ai_service)
