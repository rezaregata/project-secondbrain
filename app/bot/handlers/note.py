from telegram import Update
from telegram.ext import ContextTypes

from app.bot.deps import get_services
from app.config import get_settings


async def note_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    content = " ".join(context.args).strip()
    if not content:
        await update.message.reply_text("Usage: /note <teks catatan>")
        return

    settings = get_settings()
    services = get_services(settings)
    try:
        active = services["model"].get_active()
        note = services["note"].save_note(
            content,
            provider=active.provider if active else None,
        )
        tags_str = ", ".join([f"#{t}" for t in note.tags]) if note.tags else "None"
        reply = (
            f"✅ Catatan disimpan (#{note.id})\n"
            f"Title: {note.title}\n"
            f"Category: {note.category}\n"
            f"Tags: {tags_str}"
        )
        await update.message.reply_text(reply)
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal menyimpan catatan: {exc}")
    finally:
        services["session"].close()


async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args).strip()
    if not query:
        await update.message.reply_text("Usage: /find <kata kunci>")
        return

    settings = get_settings()
    services = get_services(settings)
    try:
        active = services["model"].get_active()
        notes = services["note"].find_similar(
            query,
            limit=5,
            provider=active.provider if active else None,
        )
        if not notes:
            await update.message.reply_text("Tidak ada catatan yang cocok.")
            return

        lines = ["🔍 Hasil pencarian:"]
        for note in notes:
            date_str = note.created_at.strftime("%Y-%m-%d")
            title = note.title or "Tanpa Judul"
            lines.append(f"• [#{note.id} {date_str}] {title}")
        await update.message.reply_text("\n".join(lines))
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal mencari: {exc}")
    finally:
        services["session"].close()


async def notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    services = get_services(settings)
    try:
        notes = services["note"].get_all_notes()
        if not notes:
            await update.message.reply_text("Belum ada catatan.")
            return

        lines = ["📋 Daftar Catatan:"]
        for note in notes:
            date_str = note.created_at.strftime("%Y-%m-%d")
            title = note.title or "Tanpa Judul"
            lines.append(f"• [#{note.id} {date_str}] {title}")
        await update.message.reply_text("\n".join(lines))
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal mengambil catatan: {exc}")
    finally:
        services["session"].close()


async def tags_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    services = get_services(settings)
    try:
        tags = services["note"].get_all_tags()
        if not tags:
            await update.message.reply_text("Belum ada tag yang tersimpan.")
            return

        lines = ["🏷️ Daftar Tag:"]
        for tag in tags:
            lines.append(f"• #{tag}")
        await update.message.reply_text("\n".join(lines))
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal mengambil tag: {exc}")
    finally:
        services["session"].close()


async def tag_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tag = " ".join(context.args).strip()
    if not tag:
        await update.message.reply_text("Usage: /tag <nama_tag>")
        return

    # Hilangkan tanda # jika user mengetiknya
    tag = tag.lstrip('#')

    settings = get_settings()
    services = get_services(settings)
    try:
        notes = services["note"].get_notes_by_tag(tag)
        if not notes:
            await update.message.reply_text(f"Tidak ada catatan dengan tag #{tag}.")
            return

        lines = [f"🏷️ Catatan dengan tag #{tag}:"]
        for note in notes:
            date_str = note.created_at.strftime("%Y-%m-%d")
            title = note.title or "Tanpa Judul"
            lines.append(f"• [#{note.id} {date_str}] {title}")
        await update.message.reply_text("\n".join(lines))
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal mengambil catatan: {exc}")
    finally:
        services["session"].close()


async def read_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /read <id_catatan>")
        return

    try:
        note_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID catatan harus berupa angka.")
        return

    settings = get_settings()
    services = get_services(settings)
    try:
        note = services["note"].get_note_by_id(note_id)
        if not note:
            await update.message.reply_text(f"❌ Catatan dengan ID {note_id} tidak ditemukan.")
            return

        date_str = note.created_at.strftime("%Y-%m-%d %H:%M:%S")
        tags_str = ", ".join([f"#{t}" for t in note.tags]) if note.tags else "None"
        title = note.title or "Tanpa Judul"
        category = note.category or "Uncategorized"

        reply = (
            f"📄 {title.upper()}\n"
            f"📅 {date_str} | 🗂️ {category}\n"
            f"🏷️ {tags_str}\n"
            f"{'-'*20}\n"
            f"{note.content}"
        )
        await update.message.reply_text(reply)
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal membaca catatan: {exc}")
    finally:
        services["session"].close()
