from telegram import Update
from telegram.ext import ContextTypes

from app.bot.deps import get_services
from app.config import get_settings


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = " ".join(context.args).strip()
    if not question:
        await update.message.reply_text("Usage: /ask <pertanyaan>")
        return

    settings = get_settings()
    services = get_services(settings)
    try:
        active = services["model"].get_active()
        provider = active.provider if active else settings.ai_provider
        model = active.model_name if active else None

        await update.message.reply_text("🤔 Sedang memproses...")

        notes = services["note"].find_similar(
            question, limit=5, provider=provider
        )
        context_text = services["note"].format_notes_context(notes)

        answer = services["ai"].chat(
            question,
            context=context_text or None,
            provider=provider,
            model=model,
        )
        await update.message.reply_text(answer)
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal menjawab: {exc}")
    finally:
        services["session"].close()
