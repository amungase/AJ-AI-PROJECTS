"""
Advanced Kite Connect Wrapper supporting Equity, Derivatives, and Commodity resolution.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

from kiteconnect import KiteConnect

logger = logging.getLogger(__name__)


class KiteService:
    def __init__(self, api_key: str, access_token: str, dry_run: bool = True) -> None:
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        self.dry_run = dry_run
        self._instruments_cache: dict[str, list[dict[str, Any]]] = {}

    def _load_instruments(self, exchange: str) -> list[dict[str, Any]]:
        if exchange not in self._instruments_cache:
            logger.info(f"Downloading reference instrument matrix for exchange: {exchange}...")
            self._instruments_cache[exchange] = self.kite.instruments(exchange)
        return self._instruments_cache[exchange]

    def resolve_any_symbol(self, query: str, exchange: str) -> Optional[dict[str, Any]]:
        """Intelligently resolves natural phrases to trading symbols across NSE, NFO, and MCX."""
        q = query.strip().lower()
        instruments = self._load_instruments(exchange)
        
        tokens = re.findall(r'[a-z0-9]+', q)
        if not tokens:
            return None

        fluff_words = {"future", "futures", "contract", "contracts", "option", "options", "call", "put"}
        tokens = [t for t in tokens if t not in fluff_words]

        months_map = {
            "january": "jan", "february": "feb", "march": "mar", "april": "apr",
            "june": "jun", "july": "jul", "august": "aug", "september": "sep",
            "october": "oct", "november": "nov", "december": "dec"
        }
        tokens = [months_map[t] if t in months_map else t for t in tokens]

        candidates: list[dict[str, Any]] = []

        for inst in instruments:
            trading_sym = (inst.get("tradingsymbol") or "").lower()
            match_count = sum(1 for token in tokens if token in trading_sym)
            if match_count == len(tokens):
                candidates.append(inst)

        if not candidates:
            return None

        if exchange == "MCX":
            futs = [c for c in candidates if "fut" in (c.get("instrument_type") or "").lower()]
            if futs:
                futs.sort(key=lambda x: len(x["tradingsymbol"]))
                return futs[0]
        elif exchange == "NFO":
            if "ce" in q or "call" in q:
                ce_opts = [c for c in candidates if (c.get("instrument_type") or "").upper() == "CE"]
                if ce_opts: return ce_opts[0]
            elif "pe" in q or "put" in q:
                pe_opts = [c for c in candidates if (c.get("instrument_type") or "").upper() == "PE"]
                if pe_opts: return pe_opts[0]

        return candidates[0]

    def format_margins(self) -> str:
        margins = self.kite.margins()
        lines = ["📊 *Margin Summary Report*\n"]
        for segment in ("equity", "commodity"):
            block = margins.get(segment) or {}
            if not block: continue
            net = block.get("net", 0)
            avail = (block.get("available") or {}).get("live_balance", 0)
            lines.append(f"*{segment.upper()} SEGMENT*\n  • Net Value: ₹{net:,.2f}\n  • Live Available Cash: ₹{avail:,.2f}\n")
        return "\n".join(lines)

    def format_holdings(self) -> str:
        holdings = self.kite.holdings()
        if not holdings: return "No active demat holdings found."
        lines = ["📁 *Live Equity Portfolio Holdings*\n"]
        for h in holdings[:15]:
            lines.append(f"• *{h.get('tradingsymbol')}*: {h.get('quantity')} Qty | Avg Price: ₹{h.get('average_price'):,.2f} | Current P&L: ₹{h.get('pnl'):,.2f}")
        return "\n".join(lines)

    def format_positions(self) -> str:
        positions = self.kite.positions()
        net = positions.get("net") or []
        active = [p for p in net if p.get("quantity") != 0]
        if not active: return "No open active trading positions."
        lines = ["📈 *Active Derivative & Margin Positions*\n"]
        for p in active:
            lines.append(f"• *{p.get('tradingsymbol')}* ({p.get('product')}): {p.get('quantity')} Qty | Net Cost: ₹{p.get('average_price'):,.2f} | Live P&L: ₹{p.get('pnl'):,.2f}")
        return "\n".join(lines)

    def format_orders(self) -> str:
        orders = self.kite.orders()
        open_orders = [o for o in orders if o.get("status") in ("OPEN", "TRIGGER PENDING")]
        if not open_orders: return "No pending open orders found."
        lines = ["📝 *Pending Open Orders Table*\n"]
        for o in open_orders[:15]:
            lines.append(f"• {o.get('tradingsymbol')} | {o.get('transaction_type')} {o.get('order_type')} | Qty: {o.get('quantity')} @ ₹{o.get('price')} | [{o.get('status')}]")
        return "\n".join(lines)

    def place_dynamic_order(self, *, exchange: str, tradingsymbol: str, transaction_type: str, quantity: int, order_type: str, product: str, price: Optional[float] = None) -> str:
        params: dict[str, Any] = {
            "variety": self.kite.VARIETY_REGULAR, "exchange": exchange, "tradingsymbol": tradingsymbol,
            "transaction_type": transaction_type.upper(), "quantity": int(quantity), "product": product,
            "order_type": order_type.upper(), "validity": self.kite.VALIDITY_DAY,
        }
        if order_type.upper() == "LIMIT":
            if price is None: raise ValueError("Limit orders require a target boundary price execution parameter.")
            params["price"] = float(price)

        if self.dry_run:
            return (
                f"🧪 *DRY RUN MOCK TRANSACTION LOGGED*\n"
                f"Exchange: `{exchange}`\n"
                f"Action: `{transaction_type.upper()}` {quantity} lots/shares of `{tradingsymbol}`\n"
                f"Execution Type: `{order_type}`" + (f" Target Limit: ₹{price}" if price else "") + f" [{product}]\n\n"
                f"_Set DRY_RUN=false inside your configuration .env to pass this to the market live exchange._"
            )

        order_id = self.kite.place_order(**params)
        return f"✅ Order successfully accepted by Exchange. Reference ID: `{order_id}`"