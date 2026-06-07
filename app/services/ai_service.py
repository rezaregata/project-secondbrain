import httpx

from app.config import Settings


class AIService:
    SYSTEM_PROMPT = (
        "Kamu adalah asisten pribadi Second Brain. "
        "Jawab dalam Bahasa Indonesia kecuali diminta lain. "
        "Gunakan konteks catatan pengguna jika tersedia."
    )

    def __init__(self, settings: Settings):
        self.settings = settings

    def chat(
        self,
        user_message: str,
        context: str | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> str:
        provider = (provider or self.settings.ai_provider).lower()
        prompt = self._build_prompt(user_message, context)

        if provider == "ollama":
            return self._ollama_chat(prompt, model or self.settings.ollama_chat_model)
        if provider == "openai":
            return self._openai_chat(prompt, model or self.settings.openai_chat_model)
        if provider == "gemini":
            return self._gemini_chat(prompt, model or self.settings.gemini_chat_model)
        if provider == "groq":
            return self._groq_chat(prompt, model or self.settings.groq_chat_model)

        raise ValueError(f"Unsupported AI provider: {provider}")

    def extract_note_metadata(
        self,
        content: str,
        provider: str | None = None,
        model: str | None = None,
    ) -> dict:
        import json
        import re

        prompt = (
            "Ekstrak metadata dari teks catatan berikut.\n"
            "Format balasan HARUS HANYA berupa JSON valid tanpa markdown (seperti ```json) dan tanpa penjelasan lain.\n"
            "JSON harus memiliki struktur persis seperti ini:\n"
            '{\n'
            '  "title": "Judul Catatan (maks 255 karakter)",\n'
            '  "category": "Kategori Umum (misal: Programming, Investasi, Project, dll)",\n'
            '  "tags": ["tag1", "tag2", "tag3"]\n'
            '}\n\n'
            f"Teks catatan:\n{content}"
        )

        response = self.chat(user_message=prompt, provider=provider, model=model)
        
        try:
            # Bersihkan jika LLM masih membandel memberikan markdown code block
            cleaned = re.sub(r"```json\s*", "", response)
            cleaned = re.sub(r"```\s*", "", cleaned)
            return json.loads(cleaned.strip())
        except Exception:
            return {
                "title": "Catatan Tanpa Judul",
                "category": "Uncategorized",
                "tags": []
            }

    def _build_prompt(self, user_message: str, context: str | None) -> str:
        if not context:
            return user_message
        return (
            "Berikut catatan relevan dari knowledge base pengguna:\n\n"
            f"{context}\n\n"
            f"Pertanyaan: {user_message}"
        )

    def _ollama_chat(self, prompt: str, model: str) -> str:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/chat"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json()["message"]["content"]

    def _openai_chat(self, prompt: str, model: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""

    def _gemini_chat(self, prompt: str, model: str) -> str:
        import google.generativeai as genai

        genai.configure(api_key=self.settings.gemini_api_key)
        gemini_model = genai.GenerativeModel(model)
        response = gemini_model.generate_content(
            f"{self.SYSTEM_PROMPT}\n\n{prompt}"
        )
        return response.text or ""

    def _groq_chat(self, prompt: str, model: str) -> str:
        from groq import Groq

        client = Groq(api_key=self.settings.groq_api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""
