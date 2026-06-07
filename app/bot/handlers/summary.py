from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.deps import get_services
from app.config import get_settings


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    services = get_services(settings)
    try:
        since = datetime.utcnow() - timedelta(days=7)
        notes = services["note"].get_notes_since(since)
        tasks = services["task"].get_tasks_since(since)
        completed = services["task"].get_completed_since(since)
        trades = services["investment"].get_recent_trades(limit=20)
        recent_trades = [t for t in trades if t.created_at >= since]

        lines = ["📊 *Ringkasan Mingguan*\n"]

        lines.append(f"📝 Catatan baru: {len(notes)}")
        if notes:
            for note in notes[:5]:
                preview = note.content[:80] + ("..." if len(note.content) > 80 else "")
                lines.append(f"  • {preview}")

        lines.append(f"\n✅ Task selesai: {len(completed)} / {len(tasks)} total")
        if completed:
            for task in completed[:5]:
                lines.append(f"  • {task.task}")

        lines.append(f"\n💰 Transaksi investasi: {len(recent_trades)}")
        if recent_trades:
            for trade in recent_trades[:5]:
                lines.append(
                    f"  • {trade.action} {trade.symbol} "
                    f"{trade.quantity} @ Rp{float(trade.price):,.0f}"
                )

        if notes:
            topics = _extract_topics([n.content for n in notes])
            if topics:
                lines.append("\n🔥 Topik sering muncul:")
                for topic, count in topics[:5]:
                    lines.append(f"  • {topic} ({count}x)")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal membuat ringkasan: {exc}")
    finally:
        services["session"].close()


def _extract_topics(contents: list[str]) -> list[tuple[str, int]]:
    from collections import Counter

    words: list[str] = []
    stopwords = {
        "dan", "atau", "yang", "dengan", "untuk", "dari", "pada", "di", "ke",
        "the", "a", "an", "is", "are", "was", "to", "of", "in", "on", "saya",
        "ini", "itu", "ada", "tidak", "juga", "akan", "sudah", "belajar",
    }
    for content in contents:
        for word in content.lower().split():
            cleaned = word.strip(".,!?;:\"'()[]{}")
            if len(cleaned) > 3 and cleaned not in stopwords:
                words.append(cleaned)
    return Counter(words).most_common(10)
