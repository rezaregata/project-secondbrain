from telegram import Update
from telegram.ext import ContextTypes

from app.bot.deps import get_services
from app.config import get_settings


async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    services = get_services(settings)
    try:
        if context.args:
            model_name = context.args[0]
            config = services["model"].set_active(model_name)
            await update.message.reply_text(
                f"✅ Model aktif: {config.provider}/{config.model_name}"
            )
        else:
            text = services["model"].format_active()
            await update.message.reply_text(text)
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal: {exc}")
    finally:
        services["session"].close()


async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    services = get_services(settings)
    try:
        text = services["model"].list_models()
        await update.message.reply_text(text)
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal: {exc}")
    finally:
        services["session"].close()
