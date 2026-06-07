import httpx

from app.config import Settings


class EmbeddingService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def embed(self, text: str, provider: str | None = None, model: str | None = None) -> list[float]:
        provider = (provider or self.settings.ai_provider).lower()

        if provider == "ollama":
            return self._ollama_embed(text, model or self.settings.ollama_embed_model)
        if provider == "openai":
            return self._openai_embed(text, model or self.settings.openai_embed_model)
        if provider == "gemini":
            return self._gemini_embed(text, model or self.settings.gemini_embed_model)

        raise ValueError(f"Unsupported embedding provider: {provider}")

    def _ollama_embed(self, text: str, model: str) -> list[float]:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/embeddings"
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json={"model": model, "prompt": text})
            response.raise_for_status()
            return response.json()["embedding"]

    def _openai_embed(self, text: str, model: str) -> list[float]:
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.embeddings.create(model=model, input=text)
        return response.data[0].embedding

    def _gemini_embed(self, text: str, model: str) -> list[float]:
        import google.generativeai as genai

        genai.configure(api_key=self.settings.gemini_api_key)
        result = genai.embed_content(model=f"models/{model}", content=text)
        return result["embedding"]
