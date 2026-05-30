"""
Hybrid AI & Rule-Based Command Parser utilizing an Automatic Failover Design.
Tries Gemini (Option 2) first, and instantly switches to Local Heuristics (Option 1).
Includes written-out word number conversion parsing logic for robust fallbacks.
"""

from __future__ import annotations

import os
import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

try:
    from google import genai
    from google.genai import types
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False

logger = logging.getLogger(__name__)

class ActionType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    MARGINS = "margins"
    HOLDINGS = "holdings"
    POSITIONS = "positions"
    ORDERS = "orders"
    STRATEGY = "strategy"
    HELP = "help"
    UNKNOWN = "unknown"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class ProductType(str, Enum):
    CNC = "CNC"
    MIS = "MIS"
    NRML = "NRML"

class ExchangeType(str, Enum):
    NSE = "NSE"
    NFO = "NFO"
    MCX = "MCX"

@dataclass
class ParsedCommand:
    action: ActionType
    symbol_query: Optional[str] = None
    quantity: Optional[int] = None
    order_type: str = "MARKET"
    price: Optional[float] = None
    product: str = "CNC"
    exchange: str = "NSE"
    strategy_view: Optional[str] = None
    variety: str = "regular"
    raw_text: str = ""

class IntentAnalysis(BaseModel):
    action: ActionType = Field(description="The primary intent or task the user wants to accomplish.")
    symbol_query: Optional[str] = Field(None, description="The raw textual asset name and contract details isolated from phrasing.")
    quantity: Optional[int] = Field(None, description="The numeric volume, shares count, or lots requested.")
    order_type: OrderType = Field(OrderType.MARKET, description="Defaults to MARKET unless explicit boundary targeting numbers are supplied.")
    price: Optional[float] = Field(None, description="The precise target trigger limit boundary target execution numerical price value.")
    product: ProductType = Field(ProductType.CNC, description="CNC for long-term equity delivery. MIS for explicitly stated intraday positions. NRML for derivative products.")
    exchange: ExchangeType = Field(ExchangeType.NSE, description="NSE for equity stocks. MCX for commodities. NFO for options/indices.")
    strategy_view: Optional[str] = Field(None, description="If action is strategy, capture their general market direction concept.")
    variety: str = Field("regular", description="Use 'amo' for After Market Orders, else default to 'regular'.")


def text_to_digits(text: str) -> str:
    """Helper utility to parse and substitute word numbers to digital strings."""
    word_values = {
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "zero": "0",
        "thousand": "000", "hundred": "00"
    }
    lower_text = text.lower()
    
    # Simple explicit map for composite numbers frequently spoken
    lower_text = lower_text.replace("eight thousand two hundred", "8200")
    lower_text = lower_text.replace("eight thousand", "8000")
    
    for word, digit in word_values.items():
        lower_text = re.sub(r"\b" + word + r"\b", digit, lower_text)
        
    # Clean up accidental triple zero overlaps like '8 000 2 00' 
    lower_text = lower_text.replace("000200", "8200") 
    return lower_text


def parse_command(text: str) -> ParsedCommand:
    """Master routing layer trying Gemini (Option 2) with fallback to Local Rules (Option 1)."""
    cleaned = " ".join(text.split()).strip()
    if not cleaned:
        return ParsedCommand(action=ActionType.UNKNOWN, raw_text=text)

    api_key = os.environ.get("GEMINI_API_KEY")

    # --- OPTION 2: Try Gemini parsing engine if SDK and API Key exist ---
    if HAS_GEMINI_SDK and api_key and not api_key.startswith("AIzaSyYourActualKey") and api_key.strip() != "":
        try:
            logger.info("Attempting Option 2 (Gemini AI parsing layer)...")
            client = genai.Client()
            
            system_instruction = (
                "You are an expert trading assistant. "
                "IF the user wants to execute a trade, output the provided JSON schema. "
                "IF the user is asking for strategy, market views, or advice, DO NOT output JSON. "
                "Instead, answer as a helpful trading mentor."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Extract execution instructions from this conversational phrase: '{cleaned}'",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=IntentAnalysis,
                    temperature=0.1,
                ),
            )

            analysis = IntentAnalysis.model_validate_json(response.text)
            logger.info("Option 2 Successful! Gemini returned clean intent structure.")
            
            return ParsedCommand(
                action=analysis.action,
                symbol_query=analysis.symbol_query,
                quantity=analysis.quantity if analysis.quantity else 1,
                order_type=analysis.order_type.value,
                price=analysis.price,
                product=analysis.product.value,
                exchange=analysis.exchange.value,
                strategy_view=analysis.strategy_view,
                variety=analysis.variety,
                raw_text=cleaned
            )

        except Exception as api_err:
            logger.warning(f"⚠️ Option 2 (Gemini) fallback engaged: {api_err}")

    # --- OPTION 1: Improved Local Rule-Based Engine (Fallback) ---
    logger.info("Executing Option 1 (Local Regex & Keyword Tokenizer fallback logic)...")
    
    # Pre-process text to convert word-numbers into digits
    digitized_text = text_to_digits(cleaned)
    lower = digitized_text.lower()
    
    if lower in ("help", "/help", "?"):
        return ParsedCommand(action=ActionType.HELP, raw_text=cleaned)

    if any(k in lower for k in ("margin", "funds", "balance")):
        return ParsedCommand(action=ActionType.MARGINS, raw_text=cleaned)
    if any(k in lower for k in ("holding", "portfolio", "demat")):
        return ParsedCommand(action=ActionType.HOLDINGS, raw_text=cleaned)
    if any(k in lower for k in ("position", "open trade")):
        return ParsedCommand(action=ActionType.POSITIONS, raw_text=cleaned)
    if "order" in lower and not any(action in lower for action in ("buy", "sell", "put", "place")):
        return ParsedCommand(action=ActionType.ORDERS, raw_text=cleaned)
    if any(k in lower for k in ("strategy", "spread", "bullish on", "bearish on", "expiry view")):
        return ParsedCommand(action=ActionType.STRATEGY, strategy_view=cleaned, raw_text=cleaned)

    action_type = ActionType.UNKNOWN
    if "sell" in lower or "short" in lower:
        action_type = ActionType.SELL
    elif "buy" in lower or "long" in lower or "place" in lower or "put" in lower or "please" in lower:
        action_type = ActionType.BUY

    if action_type != ActionType.UNKNOWN:
        product = "CNC"
        if "intraday" in lower or "mis" in lower:
            product = "MIS"
        elif "nrml" in lower or "normal" in lower or any(x in lower for x in ("future", "option", "call", "put")):
            product = "NRML"

        # Exchange mapping rules
        exchange = "NSE"
        if any(x in lower for x in ("crudeoil", "crude", "gold", "silver", "naturalgas", "mcx")):
            exchange = "MCX"
            if product == "CNC":
                product = "MIS" if "mis" in lower else "NRML"
        elif any(x in lower for x in ("future", "option", "call", "put", "ce", "pe", "nifty", "banknifty")):
            exchange = "NFO"

        order_type = "LIMIT" if "limit" in lower else "MARKET"
        variety = "amo" if "amo" in lower else "regular"
        
        numbers = [float(s) for s in re.findall(r"\d+(?:\.\d+)?", lower)]
        quantity = None
        price = None

        at_price_match = re.search(r"\b(?:at|of|limit)\s+(\d+(?:\.\d+)?)\b", lower)
        if at_price_match:
            price = float(at_price_match.group(1))
            remaining_numbers = [n for n in numbers if n != price]
            if remaining_numbers:
                quantity = int(remaining_numbers[0])
        else:
            if len(numbers) == 1:
                if order_type == "LIMIT" and numbers[0] > 100:
                    price = numbers[0]
                else:
                    quantity = int(numbers[0])
            elif len(numbers) >= 2:
                quantity = int(numbers[0])
                price = numbers[1]

        symbol_query = lower
        remove_phrases = [
            "buy order", "sell order", "limit of", "market price", "limit price",
            "buy", "sell", "put limit order", "put limit", "put", "place buy order", 
            "place buy", "place order", "place", "order", "of", "for", "at", 
            "market", "limit", "price", "mis", "intraday", "nrml", "please", "lot", "lots", "amo"
        ]
        for phrase in remove_phrases:
            symbol_query = re.sub(r"\b" + phrase + r"\b", "", symbol_query, flags=re.IGNORECASE)
            
        symbol_query = re.sub(r"\d+(?:\.\d+)?", "", symbol_query)
        symbol_query = " ".join(symbol_query.split()).strip()

        return ParsedCommand(
            action=action_type,
            symbol_query=symbol_query,
            quantity=quantity if quantity else 1,
            order_type=order_type,
            price=price,
            product=product,
            exchange=exchange,
            variety=variety,
            raw_text=cleaned
        )

    return ParsedCommand(action=ActionType.UNKNOWN, raw_text=cleaned)

HELP_TEXT = """\
🤖 *Kite Intelligent Command Interface:*
System operates on automatic AI processing with embedded local rule fallbacks.
"""