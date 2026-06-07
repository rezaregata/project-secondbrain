from app.config import Settings
from app.database.connection import SessionLocal
from app.services.ai_service import AIService
from app.services.embedding_service import EmbeddingService
from app.services.investment_service import InvestmentService
from app.services.model_service import ModelService
from app.services.note_service import NoteService
from app.services.task_service import TaskService


def get_services(settings: Settings):
    session = SessionLocal()
    embedding_service = EmbeddingService(settings)
    ai_service = AIService(settings)
    return {
        "session": session,
        "note": NoteService(session, embedding_service, ai_service),
        "task": TaskService(session),
        "investment": InvestmentService(session),
        "ai": ai_service,
        "embedding": embedding_service,
        "model": ModelService(session, settings),
    }
