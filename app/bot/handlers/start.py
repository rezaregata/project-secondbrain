from telegram import Update
from telegram.ext import ContextTypes

from app.bot.commands import HELP_TEXT
from app.bot.deps import get_services
from app.config import get_settings


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Halo! Saya Second Brain Bot — asisten pribadi untuk catatan, task, dan investasi.\n"
        "Ketik /help untuk melihat perintah."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")
