# 🚀 AI-Hybrid Conversational Trading Bot

An AI-powered conversational algorithmic trading engine that enables real-time trade execution through Telegram voice and text commands using Zerodha Kite Connect APIs.

This project combines Generative AI, conversational interfaces, voice processing, and rule-based failover systems to create a production-grade autonomous trading assistant.

---

# 🎯 Key Features

✅ Voice-based trading execution via Telegram
✅ AI-powered natural language trading parser
✅ Gemini AI + Local Rule-Based Failover Architecture
✅ Real-time NSE / NFO / MCX instrument resolution
✅ Dry-run simulation mode for safe testing
✅ Automated order execution through Zerodha Kite Connect
✅ Voice-to-trade workflow using SpeechRecognition + FFmpeg
✅ Intelligent options/futures contract mapping
✅ Markdown-safe Telegram response handling
✅ Authorized-user security restrictions

---

# 🧠 System Architecture


Telegram Voice/Text
        │
        ▼
telegram_kite_bot.py
        │
        ▼
command_parser.py
        │
 ┌───────────────┐
 │ Gemini AI NLP │
 └───────────────┘
        │
   (Fallback)
        ▼
Local Regex Engine
        │
        ▼
kite_service.py
        │
        ▼
Zerodha Kite Connect API
        │
        ▼
Trade Execution / Simulation


---

# ⚡ Example Commands

### Voice/Text Trading Commands


"Buy crudeoil june future MIS at 8398"

"Show my open positions"

"Place BankNifty CE intraday order"

"Close my crudeoil position"

"Show portfolio holdings"


---

# 🛠 Tech Stack

| Category           | Technologies                     |
| ------------------ | -------------------------------- |
| Language           | Python                           |
| AI/NLP             | Google Gemini AI                 |
| Trading APIs       | Zerodha Kite Connect             |
| Bot Framework      | python-telegram-bot              |
| Voice Processing   | SpeechRecognition, FFmpeg, pydub |
| Validation         | Pydantic                         |
| Environment Config | python-dotenv                    |
| Architecture       | Hybrid AI + Rule-Based System    |

---

# 📂 Project Structure


AI-Hybrid-Conversational-Trading-Bot/
│
├── command_parser.py
├── kite_service.py
├── kite_login.py
├── telegram_kite_bot.py
├── requirements.txt
├── .env.example
├── README.md


---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

bash
git clone https://github.com/amungase/AJ-AI-PROJECTS.git


---

## 2️⃣ Install Dependencies

bash
pip install -r requirements.txt


---

## 3️⃣ Configure Environment Variables

Create `.env` file:

env
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_TOKEN
TELEGRAM_ALLOWED_USER_ID=YOUR_USER_ID

KITE_API_KEY=YOUR_KITE_API_KEY
KITE_API_SECRET=YOUR_KITE_SECRET
KITE_ACCESS_TOKEN=YOUR_DAILY_ACCESS_TOKEN

GEMINI_API_KEY=YOUR_GEMINI_API_KEY

DRY_RUN=true

FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe


---

## 4️⃣ Generate Zerodha Access Token

Run:

bash
python kite_login.py


Copy generated `KITE_ACCESS_TOKEN` into `.env`.

---

## 5️⃣ Start Trading Bot

bash
python telegram_kite_bot.py


---

# 🎤 Voice Trading Workflow

1. Send voice note on Telegram
2. Bot converts speech → text
3. Gemini AI parses trading intent
4. Local failover engine validates structure
5. Zerodha API executes or simulates trade
6. Telegram returns execution response

---

# 🔥 Hybrid AI Architecture

The project uses a dual-layer parsing engine:

## Layer 1 — Gemini AI

* Understands conversational trading language
* Extracts symbols, exchanges, quantities, prices
* Maps structured JSON responses

## Layer 2 — Local Rule Engine (Failover)

* Automatically activates during:

  * API failures
  * AI quota exhaustion
  * Connectivity issues
* Ensures uninterrupted trading operations

This architecture increases reliability for production-grade trading systems.

---
# 🧪 Safety Mode

The system supports secure simulation mode:

env
DRY_RUN=true


This prevents real-money execution during testing.

To enable live trading:

env
DRY_RUN=false


---

# 🔐 Security Features

✅ Authorized Telegram user restriction
✅ Environment-based secret management
✅ Dry-run execution safeguards
✅ AI failover protection
✅ Exchange-specific validation logic

---

# 📈 Future Enhancements

* Multi-account portfolio orchestration
* AI-generated options strategies
* Autonomous risk management
* Live broker calling agent
* Advanced portfolio analytics
* Real-time market data streaming

---

# ⚠️ Disclaimer

This project is developed for educational and research purposes only.

Algorithmic trading involves financial risk.
Use responsibly and test thoroughly before enabling live trading.

The author is not responsible for any financial losses resulting from the use of this software.

---

🔗 GitHub:
[https://github.com/amungase](https://github.com/amungase)

🔗 Portfolio:
https://ajgenstudio.lovable.app/

---
