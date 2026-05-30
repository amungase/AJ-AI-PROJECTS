#!/usr/bin/env python3
"""
Telegram bot ↔ Zerodha Kite Connect bridge.
Features: Multi-leg strategy execution, context recovery for failed orders (e.g., "Place AMO order then"),
          auto-chunking for long text, and Interactive Inline Confirmation Buttons.
"""

from __future__ import annotations

import logging
import os
import sys
import tempfile
import re
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatType, ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

from command_parser import HELP_TEXT, ActionType, ParsedCommand, parse_command
from kite_service import KiteService

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()

def _env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")

def _allowed_user_id() -> int:
    raw = os.environ.get("TELEGRAM_ALLOWED_USER_ID")
    if not raw: raise RuntimeError("Set TELEGRAM_ALLOWED_USER_ID in your .env file!")
    return int(raw)

def _build_kite_service() -> KiteService:
    api_key = os.environ.get("KITE_API_KEY")
    access_token = os.environ.get("KITE_ACCESS_TOKEN")
    if not api_key or not access_token: raise RuntimeError("Missing keys in .env")
    return KiteService(api_key=api_key, access_token=access_token, dry_run=_env_bool("DRY_RUN", default=True))

KITE: KiteService | None = None
conversation_history: dict[int, list[dict[str, str]]] = {}
# Temporary storage to hold order structures awaiting interactive confirmation click
pending_orders: dict[str, list[dict]] = {}

def _is_authorized(update: Update) -> bool:
    user = update.effective_user
    if not user or (update.effective_chat and update.effective_chat.type != ChatType.PRIVATE): return False
    return user.id == _allowed_user_id()

def _track_context(user_id: int, role: str, text: str):
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append({"role": role, "text": text})
    if len(conversation_history[user_id]) > 10:
        conversation_history[user_id].pop(0)

def chunk_text(text: str, max_length: int = 4000) -> list[str]:
    if len(text) <= max_length:
        return [text]
    chunks = []
    current_chunk = ""
    for line in text.splitlines(keepends=True):
        if len(current_chunk) + len(line) > max_length:
            if current_chunk: chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            current_chunk += line
    if current_chunk: chunks.append(current_chunk.strip())
    return chunks

async def send_safe_reply(update: Update, text: str) -> None:
    chunks = chunk_text(text)
    for chunk in chunks:
        try:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await update.message.reply_text(chunk)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update): return
    await send_safe_reply(update, "Kite intelligence layer active.\n\n" + HELP_TEXT)

async def _process_user_text(update: Update, text: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert KITE is not None
    user_id = update.effective_user.id
    
    # 1. EXTENDED ORDER INTENT FILTER (Now tracking AMO modifications explicitly)
    is_execution_requested = any(k in text.lower() for k in ("place order", "execute", "buy", "sell", "trade", "amo"))
    parsed = parse_command(text)
    
    logger.info("Parsed intent: %s from input: %r", parsed.action, text)

    try:
        # --- PATH 1: Local Rules & Dashboard Reports ---
        if parsed.action in (ActionType.MARGINS, ActionType.HOLDINGS, ActionType.POSITIONS, ActionType.ORDERS, ActionType.HELP):
            if parsed.action == ActionType.HELP: reply = HELP_TEXT
            elif parsed.action == ActionType.MARGINS: reply = KITE.format_margins()
            elif parsed.action == ActionType.HOLDINGS: reply = KITE.format_holdings()
            elif parsed.action == ActionType.POSITIONS: reply = KITE.format_positions()
            elif parsed.action == ActionType.ORDERS: reply = KITE.format_orders()
            await send_safe_reply(update, reply)
            return

        # --- PATH 2 & 3: Order Pipeline With Confirmation Buttons ---
        if is_execution_requested or parsed.action in (ActionType.BUY, ActionType.SELL):
            legs_to_confirm = []
            override_variety = "regular"
            
            # Check if user wants an AMO transition contextually
            if "amo" in text.lower():
                override_variety = "amo"

            # Sub-Path A: Context-Based Retrieval via Gemini (Strategies or "Place AMO order then" conversions)
            if parsed.action == ActionType.UNKNOWN or not parsed.symbol_query or "strategy" in text.lower() or "then" in text.lower():
                if HAS_GENAI and os.environ.get("GEMINI_API_KEY"):
                    history_str = "".join([f"{m['role'].upper()}: {m['text']}\n\n" for m in conversation_history.get(user_id, [])])
                    
                    client = genai.Client()
                    extraction_prompt = (
                        f"History Context:\n{history_str}"
                        f"User command: '{text}'.\n"
                        f"Tasks:\n"
                        f"1. Look at the immediate history. If the user says something like 'Place AMO order then' or references a previous failure, look for the order details they tried to send last (e.g., Crudeoil futures, options, etc.).\n"
                        f"2. Extract those option/future legs.\n"
                        f"3. For EACH leg, return EXACTLY this template layout on a new line:\n"
                        f"BUY/SELL [Quantity] lots of [Asset Name] [Strike] [CE/PE] at [Market/Limit Price] [MIS/NRML]"
                    )
                    response = client.models.generate_content(model="gemini-2.5-flash", contents=extraction_prompt)
                    extracted_lines = [line.strip() for line in response.text.split('\n') if line.strip()]
                    logger.info("Contextual recovery parsed lines: %s", extracted_lines)
                    
                    for leg_cmd in extracted_lines:
                        if not any(k in leg_cmd.lower() for k in ("buy", "sell")): continue
                        leg_parsed = parse_command(leg_cmd)
                        if leg_parsed.action in (ActionType.BUY, ActionType.SELL) and leg_parsed.symbol_query:
                            legs_to_confirm.append(leg_parsed)
                else:
                    await send_safe_reply(update, "❌ Gemini SDK / Key required for analyzing trade context.")
                    return
            
            # Sub-Path B: Direct Single Order
            else:
                legs_to_confirm.append(parsed)

            if not legs_to_confirm:
                await send_safe_reply(update, "❌ Could not parse or isolate specific execution legs from context.")
                return

            # Package information for confirmation buttons
            tx_id = f"tx_{update.message.message_id}"
            pending_orders[tx_id] = []
            
            type_tag = "AMO Order" if override_variety == "amo" else "Regular Order"
            confirmation_msg = f"📋 *Kite {type_tag} Confirmation Required*\nPlease confirm the following details:\n\n"
            
            for index, leg in enumerate(legs_to_confirm):
                inst = KITE.resolve_any_symbol(leg.symbol_query, leg.exchange)
                symbol_resolved = inst["tradingsymbol"] if inst else leg.symbol_query
                
                pending_orders[tx_id].append({
                    "exchange": leg.exchange,
                    "tradingsymbol": symbol_resolved,
                    "transaction_type": leg.action.upper(),
                    "quantity": leg.quantity if leg.quantity else 1,
                    "order_type": leg.order_type,
                    "product": leg.product,
                    "price": leg.price,
                    "variety": override_variety
                })
                
                price_str = f" @ ₹{leg.price}" if leg.order_type == "LIMIT" else " @ Market"
                confirmation_msg += f"*{index+1}. {leg.action.upper()}* | {leg.quantity} Lot(s) | `{symbol_resolved}` ({leg.exchange}) | {leg.product} | {leg.order_type}{price_str}\n"

            # Render inline confirmation UI buttons inside Telegram
            keyboard = [
                [
                    InlineKeyboardButton("🚀 Confirm & Transmit", callback_data=f"confirm_{tx_id}"),
                    InlineKeyboardButton("❌ Abort", callback_data=f"cancel_{tx_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(confirmation_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            return

        # --- PATH 4: Conversational Brain (Market Strategy Advisory) ---
        if HAS_GENAI and os.environ.get("GEMINI_API_KEY"):
            client = genai.Client()
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are a sophisticated derivatives advisor. User query: '{text}'. Provide clear, concise strategy advice."
            )
            reply = response.text
        else:
            reply = "❌ Request not recognized as an order. Set up the Gemini API key for advisor access."

        await send_safe_reply(update, reply)

    except Exception as exc:
        logger.exception("Processing failure")
        await send_safe_reply(update, f"❌ *System Error:* {str(exc)}")
    finally:
        # Cache every message exchange sequentially to preserve transactional context
        _track_context(user_id, "user", text)
        if reply:
            _track_context(user_id, "assistant", reply)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Intercepts inline button choices."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    data = query.data
    action, tx_id = data.split('_', 1)
    
    if action == "cancel":
        pending_orders.pop(tx_id, None)
        await query.edit_message_text("❌ *Order Pipeline Aborted:* No trades were sent to Kite.", parse_mode=ParseMode.MARKDOWN)
        return
        
    if action == "confirm":
        orders = pending_orders.pop(tx_id, None)
        if not orders:
            await query.edit_message_text("⚠️ *Error:* Transaction expired or context lost.")
            return
            
        await query.edit_message_text("⚡ *Transmitting orders to Zerodha backend execution matrix...*")
        
        execution_logs = ["⚡ *Kite Execution Results:*"]
        for o in orders:
            try:
                res = KITE.place_dynamic_order(
                    exchange=o["exchange"],
                    tradingsymbol=o["tradingsymbol"],
                    transaction_type=o["transaction_type"],
                    quantity=o["quantity"],
                    order_type=o["order_type"],
                    product=o["product"],
                    price=o["price"],
                    variety=o.get("variety", "regular")
                )
                execution_logs.append(f"• {res}")
                _track_context(user_id, "assistant", f"Kite Execution Success on {o['tradingsymbol']}")
            except Exception as e:
                err_msg = f"Failure on `{o['tradingsymbol']}`: {str(e)}"
                execution_logs.append(f"• ❌ {err_msg}")
                # Save the failure reason inside history so Gemini can analyze it on subsequent followups
                _track_context(user_id, "assistant", err_msg)
                
        final_report = "\n\n".join(execution_logs)
        for chunk in chunk_text(final_report):
            await query.message.chat.send_message(chunk, parse_mode=ParseMode.MARKDOWN)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text or not _is_authorized(update): return
    await _process_user_text(update, update.message.text, context)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.voice or not _is_authorized(update): return
    await update.message.reply_text("🎤 Processing voice transmission segment...")
    voice = update.message.voice
    tmp_dir = Path(tempfile.mkdtemp(prefix="tg_voice_"))
    ogg_path = tmp_dir / f"{voice.file_unique_id}.ogg"

    try:
        tg_file = await voice.get_file()
        await tg_file.download_to_drive(custom_path=str(ogg_path))
        from pydub import AudioSegment
        import speech_recognition as sr
        wav_path = ogg_path.with_suffix(".wav")
        AudioSegment.from_file(ogg_path, format="ogg").export(wav_path, format="wav")
        recognizer = sr.Recognizer()
        with sr.AudioFile(str(wav_path)) as source: audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="en-IN").strip()
        await update.message.reply_text(f"📝 *Transcribed:* \"{text}\"", parse_mode=ParseMode.MARKDOWN)
        await _process_user_text(update, text, context)
    except Exception as exc:
        logger.exception("Voice processing error")
        await update.message.reply_text(f"Voice tracking failed: {exc}")
    finally:
        for p in tmp_dir.glob("*"):
            try: p.unlink()
            except OSError: pass
        try: tmp_dir.rmdir()
        except OSError: pass

def main() -> None:
    print("=======================================")
    print("--- INITIALIZING KITE AI TRADER BOT ---")
    print("=======================================")
    
    global KITE
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token: 
        print("CRITICAL ERROR: TELEGRAM_BOT_TOKEN missing in your .env file!")
        sys.exit(1)
        
    try:
        KITE = _build_kite_service()
        print("➡️ Kite Connection initialized successfully.")
    except Exception as exc:
        print(f"CRITICAL ERROR: Initialization of Kite Service failed: {exc}")
        sys.exit(1)
        
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    print("🚀 BOT RUNNING: Listening for Telegram messages...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()