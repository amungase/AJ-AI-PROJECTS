#!/usr/bin/env python3
"""
Telegram bot ↔ Zerodha Kite Connect bridge.
"""

from __future__ import annotations

import logging
import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatType, ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from command_parser import HELP_TEXT, ActionType, parse_command
from kite_service import KiteService

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

_ffmpeg = os.environ.get("FFMPEG_PATH")
if _ffmpeg:
    os.environ["PATH"] = str(Path(_ffmpeg).parent) + os.pathsep + os.environ.get("PATH", "")

def _env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")

def _allowed_user_id() -> int:
    raw = os.environ.get("TELEGRAM_ALLOWED_USER_ID")
    if not raw: raise RuntimeError("Set TELEGRAM_ALLOWED_USER_ID in .env")
    return int(raw)

def _build_kite_service() -> KiteService:
    api_key = os.environ.get("KITE_API_KEY")
    access_token = os.environ.get("KITE_ACCESS_TOKEN")
    if not api_key or not access_token: raise RuntimeError("Missing keys in .env")
    return KiteService(api_key=api_key, access_token=access_token, dry_run=_env_bool("DRY_RUN", default=True))

KITE: KiteService | None = None

def _is_authorized(update: Update) -> bool:
    user = update.effective_user
    if not user or (update.effective_chat and update.effective_chat.type != ChatType.PRIVATE): return False
    return user.id == _allowed_user_id()

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update): return
    await update.message.reply_text("Kite intelligence layer active.\n\n" + HELP_TEXT, parse_mode=ParseMode.MARKDOWN)

async def _process_user_text(update: Update, text: str) -> None:
    assert KITE is not None
    parsed = parse_command(text)
    logger.info("Parsed command action intent: %s from input: %r", parsed.action, text)

    try:
        if parsed.action == ActionType.HELP: reply = HELP_TEXT
        elif parsed.action == ActionType.MARGINS: reply = KITE.format_margins()
        elif parsed.action == ActionType.HOLDINGS: reply = KITE.format_holdings()
        elif parsed.action == ActionType.POSITIONS: reply = KITE.format_positions()
        elif parsed.action == ActionType.ORDERS: reply = KITE.format_orders()
        elif parsed.action in (ActionType.BUY, ActionType.SELL):
            if not parsed.symbol_query:
                reply = "Could not cleanly map or isolate target financial instrument symbol query string."
            else:
                inst = KITE.resolve_any_symbol(parsed.symbol_query, parsed.exchange)
                if not inst:
                    reply = f"Could not find matching execution asset for phrase '{parsed.symbol_query}' inside {parsed.exchange}."
                else:
                    reply = KITE.place_dynamic_order(
                        exchange=parsed.exchange, tradingsymbol=inst["tradingsymbol"],
                        transaction_type=parsed.action.upper(), quantity=parsed.quantity,
                        order_type=parsed.order_type, product=parsed.product, price=parsed.price,
                    )
        else: reply = "Command query template did not match. See instructions:\n\n" + HELP_TEXT
    except Exception as exc:
        logger.exception("Kite execution failure")
        reply = f"❌ *Kite API Handoff Exception:* {str(exc)}"

    try:
        await update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
    except Exception as parse_err:
        logger.warning(f"Markdown fallback triggered: {parse_err}")
        await update.message.reply_text(reply)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text or not _is_authorized(update): return
    await _process_user_text(update, update.message.text)

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
        await _process_user_text(update, text)
    except Exception as exc:
        logger.exception("Voice tracking crash.")
        await update.message.reply_text(f"Voice tracking failed: {exc}")
    finally:
        for p in tmp_dir.glob("*"):
            try: p.unlink()
            except OSError: pass
        try: tmp_dir.rmdir()
        except OSError: pass

def main() -> None:
    global KITE
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token: sys.exit("Missing TELEGRAM_BOT_TOKEN")
    try: KITE = _build_kite_service()
    except RuntimeError as exc: sys.exit(exc)
    
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()