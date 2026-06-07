import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_token: str

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    ai_provider: str
    ollama_base_url: str
    ollama_chat_model: str
    ollama_embed_model: str

    embedding_dimension: int

    openai_api_key: str
    openai_chat_model: str
    openai_embed_model: str

    gemini_api_key: str
    gemini_chat_model: str
    gemini_embed_model: str

    groq_api_key: str
    groq_chat_model: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


def get_settings() -> Settings:
    return Settings(
        telegram_token=os.getenv("TELEGRAM_TOKEN", ""),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_name=os.getenv("DB_NAME", "secondbrain"),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=os.getenv("DB_PASSWORD", "postgres"),
        ai_provider=os.getenv("AI_PROVIDER", "ollama").lower(),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_chat_model=os.getenv("OLLAMA_CHAT_MODEL", "llama3.2"),
        ollama_embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "768")),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        openai_embed_model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_chat_model=os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash"),
        gemini_embed_model=os.getenv("GEMINI_EMBED_MODEL", "text-embedding-004"),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_chat_model=os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile"),
    )
