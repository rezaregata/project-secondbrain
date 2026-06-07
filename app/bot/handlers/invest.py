from decimal import Decimal, InvalidOperation

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.deps import get_services
from app.config import get_settings


async def invest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 4:
        await update.message.reply_text(
            "Usage:\n"
            "/invest buy <symbol> <harga> <qty>\n"
            "/invest sell <symbol> <harga> <qty>"
        )
        return

    action = context.args[0].lower()
    if action not in ("buy", "sell"):
        await update.message.reply_text("Action harus 'buy' atau 'sell'.")
        return

    symbol = context.args[1].upper()
    try:
        price = Decimal(context.args[2])
        quantity = Decimal(context.args[3])
    except InvalidOperation:
        await update.message.reply_text("Harga dan quantity harus berupa angka.")
        return

    note = " ".join(context.args[4:]).strip() or None

    settings = get_settings()
    services = get_services(settings)
    try:
        trade = services["investment"].record_trade(action, symbol, price, quantity, note)
        emoji = "🟢" if action == "buy" else "🔴"
        await update.message.reply_text(
            f"{emoji} {action.upper()} {symbol} "
            f"{quantity} @ Rp{price:,.0f} (#{trade.id})"
        )
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal mencatat: {exc}")
    finally:
        services["session"].close()


async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    services = get_services(settings)
    try:
        text = services["investment"].format_portfolio()
        recent = services["investment"].get_recent_trades(limit=5)
        if recent:
            text += "\n\n📜 Transaksi terakhir:"
            for trade in recent:
                text += (
                    f"\n• {trade.action} {trade.symbol} "
                    f"{trade.quantity} @ Rp{Decimal(str(trade.price)):,.0f}"
                )
        await update.message.reply_text(text)
    except Exception as exc:
        await update.message.reply_text(f"❌ Gagal memuat portfolio: {exc}")
    finally:
        services["session"].close()
