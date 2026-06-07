from datetime import datetime, timedelta

from sqlalchemy import select, text, func
from sqlalchemy.orm import Session

from app.database.models import Note
from app.services.embedding_service import EmbeddingService
from app.services.ai_service import AIService


class NoteService:
    def __init__(self, session: Session, embedding_service: EmbeddingService, ai_service: AIService):
        self.session = session
        self.embedding_service = embedding_service
        self.ai_service = ai_service

    def save_note(
        self, content: str, provider: str | None = None, model: str | None = None
    ) -> Note:
        # Extract metadata
        metadata = self.ai_service.extract_note_metadata(content, provider=provider, model=model)
        
        # Create embedding
        embedding = self.embedding_service.embed(content, provider=provider, model=model)
        
        note = Note(
            content=content, 
            embedding=embedding,
            title=metadata.get("title"),
            category=metadata.get("category"),
            tags=metadata.get("tags", []),
            source="telegram"
        )
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note

    def find_similar(
        self,
        query: str,
        limit: int = 5,
        provider: str | None = None,
        model: str | None = None,
    ) -> list[Note]:
        embedding = self.embedding_service.embed(query, provider=provider, model=model)
        embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"

        sql = text(
            """
            SELECT id, content, created_at,
                   1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
            FROM notes
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
            """
        )
        rows = self.session.execute(
            sql, {"embedding": embedding_str, "limit": limit}
        ).fetchall()

        notes: list[Note] = []
        for row in rows:
            note = self.session.get(Note, row.id)
            if note:
                notes.append(note)
        return notes

    def get_notes_since(self, since: datetime) -> list[Note]:
        stmt = (
            select(Note)
            .where(Note.created_at >= since)
            .order_by(Note.created_at.desc())
        )
        return list(self.session.scalars(stmt).all())

    def format_notes_context(self, notes: list[Note]) -> str:
        if not notes:
            return ""
        lines = []
        for i, note in enumerate(notes, start=1):
            date_str = note.created_at.strftime("%Y-%m-%d")
            title_str = f" [{note.title}]" if note.title else ""
            lines.append(f"{i}. [{date_str}]{title_str} {note.content}")
        return "\n".join(lines)

    def get_recent_notes(self, days: int = 7) -> list[Note]:
        since = datetime.utcnow() - timedelta(days=days)
        return self.get_notes_since(since)

    def get_all_notes(self) -> list[Note]:
        stmt = select(Note).order_by(Note.created_at.desc())
        return list(self.session.scalars(stmt).all())

    def get_all_tags(self) -> list[str]:
        # Unnest array and get unique tags
        sql = text("SELECT DISTINCT unnest(tags) as tag FROM notes WHERE tags IS NOT NULL")
        rows = self.session.execute(sql).fetchall()
        return [row.tag for row in rows if row.tag]

    def get_notes_by_tag(self, tag: str) -> list[Note]:
        stmt = select(Note).where(Note.tags.any(tag)).order_by(Note.created_at.desc())
        return list(self.session.scalars(stmt).all())

    def get_note_by_id(self, note_id: int) -> Note | None:
        return self.session.get(Note, note_id)
