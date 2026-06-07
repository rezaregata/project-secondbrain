from telegram import Update
from telegram.ext import ContextTypes

from app.bot.deps import get_services
from app.config import get_settings


async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    task_text = " ".join(context.args).strip()
    if not task_text:
        await update.message.reply_text("Usage: /task <teks task>")
        return

    settings = get_settings()
    services = get_services(settings)
    try:
        task = services["task"].add_task(task_text)
        await update.message.reply_text(f"✅ Task ditambahkan (#{task.id}): {task.task}")
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal menambah task: {exc}")
    finally:
        services["session"].close()


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    services = get_services(settings)
    try:
        tasks = services["task"].get_today_tasks()
        text = services["task"].format_task_list(tasks)
        await update.message.reply_text(f"📋 Task hari ini:\n{text}")
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal memuat task: {exc}")
    finally:
        services["session"].close()


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /done <task_id>")
        return

    try:
        task_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Task ID harus berupa angka.")
        return

    settings = get_settings()
    services = get_services(settings)
    try:
        task = services["task"].mark_done(task_id)
        if not task:
            await update.message.reply_text(f"Task #{task_id} tidak ditemukan.")
            return
        await update.message.reply_text(f"✅ Task #{task_id} ditandai selesai.")
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal: {exc}")
    finally:
        services["session"].close()
