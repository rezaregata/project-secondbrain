from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config import Settings
from app.database.models import ModelConfig


AVAILABLE_MODELS: dict[str, list[str]] = {
    "ollama": ["llama3.2", "qwen3", "mistral", "gemma2"],
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4.1"],
    "gemini": ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.0-flash-lite"],
    "groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
}


class ModelService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def get_active(self) -> ModelConfig | None:
        stmt = select(ModelConfig).where(ModelConfig.active.is_(True)).limit(1)
        active = self.session.scalars(stmt).first()
        if active:
            return active
        return self._ensure_default()

    def _ensure_default(self) -> ModelConfig:
        config = ModelConfig(
            provider=self.settings.ai_provider,
            model_name=self._default_model_for_provider(self.settings.ai_provider),
            active=True,
        )
        self.session.add(config)
        self.session.commit()
        self.session.refresh(config)
        return config

    def _default_model_for_provider(self, provider: str) -> str:
        defaults = {
            "ollama": self.settings.ollama_chat_model,
            "openai": self.settings.openai_chat_model,
            "gemini": self.settings.gemini_chat_model,
            "groq": self.settings.groq_chat_model,
        }
        return defaults.get(provider, self.settings.ollama_chat_model)

    def set_active(self, model_name: str) -> ModelConfig:
        provider = self._resolve_provider(model_name)
        self.session.execute(update(ModelConfig).values(active=False))
        self.session.commit()

        stmt = select(ModelConfig).where(
            ModelConfig.provider == provider,
            ModelConfig.model_name == model_name,
        )
        existing = self.session.scalars(stmt).first()

        if existing:
            existing.active = True
            config = existing
        else:
            config = ModelConfig(provider=provider, model_name=model_name, active=True)
            self.session.add(config)

        self.session.commit()
        self.session.refresh(config)
        return config

    def _resolve_provider(self, model_name: str) -> str:
        for provider, models in AVAILABLE_MODELS.items():
            if model_name in models:
                return provider
        return self.settings.ai_provider

    def list_models(self) -> str:
        active = self.get_active()
        lines = ["📋 Model tersedia:"]
        for provider, models in AVAILABLE_MODELS.items():
            lines.append(f"\n{provider.upper()}:")
            for model in models:
                marker = " ✓" if active and active.model_name == model else ""
                lines.append(f"  • {model}{marker}")
        if active:
            lines.append(f"\nAktif: {active.provider}/{active.model_name}")
        return "\n".join(lines)

    def format_active(self) -> str:
        active = self.get_active()
        if not active:
            return "Belum ada model aktif."
        return f"Model aktif: {active.provider}/{active.model_name}"
