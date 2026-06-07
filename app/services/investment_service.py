from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Investment


class InvestmentService:
    def __init__(self, session: Session):
        self.session = session

    def record_trade(
        self,
        action: str,
        symbol: str,
        price: Decimal,
        quantity: Decimal,
        note: str | None = None,
    ) -> Investment:
        investment = Investment(
            action=action.upper(),
            symbol=symbol.upper(),
            price=price,
            quantity=quantity,
            note=note,
        )
        self.session.add(investment)
        self.session.commit()
        self.session.refresh(investment)
        return investment

    def get_all_trades(self) -> list[Investment]:
        stmt = select(Investment).order_by(Investment.created_at.desc())
        return list(self.session.scalars(stmt).all())

    def get_portfolio(self) -> dict[str, dict]:
        trades = self.get_all_trades()
        holdings: dict[str, dict] = defaultdict(
            lambda: {"quantity": Decimal("0"), "total_cost": Decimal("0"), "trades": 0}
        )

        for trade in trades:
            symbol = trade.symbol or "UNKNOWN"
            qty = Decimal(str(trade.quantity or 0))
            price = Decimal(str(trade.price or 0))

            if trade.action == "BUY":
                holdings[symbol]["quantity"] += qty
                holdings[symbol]["total_cost"] += qty * price
                holdings[symbol]["trades"] += 1
            elif trade.action == "SELL":
                holdings[symbol]["quantity"] -= qty
                if holdings[symbol]["quantity"] > 0:
                    avg = holdings[symbol]["total_cost"] / (
                        holdings[symbol]["quantity"] + qty
                    )
                    holdings[symbol]["total_cost"] = (
                        holdings[symbol]["quantity"] * avg
                    )
                else:
                    holdings[symbol]["total_cost"] = Decimal("0")
                holdings[symbol]["trades"] += 1

        portfolio = {}
        for symbol, data in holdings.items():
            if data["quantity"] > 0:
                avg_price = (
                    data["total_cost"] / data["quantity"]
                    if data["quantity"] > 0
                    else Decimal("0")
                )
                portfolio[symbol] = {
                    "quantity": data["quantity"],
                    "avg_price": avg_price,
                    "total_cost": data["total_cost"],
                }
        return portfolio

    def format_portfolio(self) -> str:
        portfolio = self.get_portfolio()
        if not portfolio:
            return "Portfolio kosong."

        lines = ["📊 Portfolio:"]
        for symbol, data in sorted(portfolio.items()):
            lines.append(
                f"• {symbol}: {data['quantity']} lot @ avg Rp{data['avg_price']:,.0f} "
                f"(total Rp{data['total_cost']:,.0f})"
            )
        return "\n".join(lines)

    def get_recent_trades(self, limit: int = 10) -> list[Investment]:
        stmt = select(Investment).order_by(Investment.created_at.desc()).limit(limit)
        return list(self.session.scalars(stmt).all())
