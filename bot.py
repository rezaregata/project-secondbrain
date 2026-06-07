import logging
import sys

from telegram.ext import Application, CommandHandler

from app.bot.handlers.ask import ask_command
from app.bot.handlers.invest import invest_command, portfolio_command
from app.bot.handlers.model import model_command, models_command
from app.bot.handlers.note import find_command, note_command, notes_command, tags_command, tag_command, read_command
from app.bot.handlers.start import help_command, start_command
from app.bot.handlers.summary import summary_command
from app.bot.handlers.task import done_command, task_command, today_command
from app.config import get_settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def setup_application() -> Application:
    settings = get_settings()

    if not settings.telegram_token:
        logger.error("TELEGRAM_TOKEN belum diset di .env")
        sys.exit(1)

    app = Application.builder().token(settings.telegram_token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("note", note_command))
    app.add_handler(CommandHandler("notes", notes_command))
    app.add_handler(CommandHandler("read", read_command))
    app.add_handler(CommandHandler("find", find_command))
    app.add_handler(CommandHandler("tags", tags_command))
    app.add_handler(CommandHandler("tag", tag_command))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CommandHandler("task", task_command))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("done", done_command))
    app.add_handler(CommandHandler("invest", invest_command))
    app.add_handler(CommandHandler("portfolio", portfolio_command))
    app.add_handler(CommandHandler("model", model_command))
    app.add_handler(CommandHandler("models", models_command))
    app.add_handler(CommandHandler("summary", summary_command))
    
    return app


def main() -> None:
    app = setup_application()
    logger.info("Second Brain Bot starting in standalone mode...")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
