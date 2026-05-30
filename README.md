# 🚀 AI-Hybrid Conversational Trading Assistant

An AI-powered conversational trading assistant that enables real-time trade execution through Telegram voice and text commands using Zerodha Kite Connect APIs.

This project combines Generative AI, conversational interfaces, voice processing, broker integrations, and rule-based failover systems to demonstrate how natural language can be used to interact with trading platforms.

The project is intended for educational, research, and software engineering demonstration purposes.

---

# 🎯 Key Features

✅ Voice-based trading execution via Telegram

✅ AI-powered natural language command parsing

✅ Gemini AI + Local Rule-Based Failover Architecture

✅ Real-time NSE / NFO / MCX instrument resolution

✅ Dry-run simulation mode for safe testing

✅ Automated order placement through Zerodha Kite Connect

✅ Voice-to-trade workflow using SpeechRecognition + FFmpeg

✅ Intelligent options and futures contract mapping

✅ Portfolio insights and holdings summaries

✅ Educational strategy exploration based on user-defined market assumptions

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

"Provide a summary of my current portfolio"

"Explain option strategy structures commonly associated with a bearish market outlook"


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

1. Send a voice note or text command on Telegram
2. Bot converts speech to text
3. Gemini AI interprets user intent
4. Local failover engine validates command structure
5. Zerodha API executes or simulates the requested action
6. Telegram returns execution or portfolio response

Users remain responsible for reviewing and validating all trade instructions and investment decisions.

---

# 🔥 Hybrid AI Architecture

The project uses a dual-layer parsing engine.

## Layer 1 — Gemini AI

* Understands conversational trading language
* Extracts symbols, exchanges, quantities, prices
* Maps structured JSON responses

## Layer 2 — Local Rule Engine (Failover)

Automatically activates during:

* API failures
* AI quota exhaustion
* Connectivity issues

Ensures uninterrupted command processing and workflow continuity.

This architecture increases reliability and resiliency for conversational broker integrations.

---

# 🧪 Safety Mode

The system supports secure simulation mode.

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


# 📚 Educational Use Notice

This project demonstrates conversational AI, voice interfaces, broker API integrations, and workflow automation within trading environments.

Any market commentary, portfolio insights, strategy discussions, or AI-generated outputs are provided solely for educational and informational purposes.

The software does not provide investment advice, trading recommendations, research reports, portfolio management services, or financial advisory services.

Users are solely responsible for evaluating any information produced by the system and for making their own trading and investment decisions.

---

# ⚠️ Disclaimer

This project is an educational and research demonstration of AI-powered conversational interfaces integrated with broker APIs.

The software is not intended to provide investment advice, trading recommendations, financial research, portfolio management, or advisory services.

Any market discussions, strategy examples, portfolio analytics, or AI-generated outputs are illustrative and informational only.

Trading and investing involve substantial financial risk. Users should conduct their own research and seek professional advice where appropriate before making investment decisions.

The author assumes no responsibility for any financial losses, damages, or consequences arising from the use of this software.

---

## 🔗 Portfolio

https://ajgenstudio.lovable.app/

## 🔗 GitHub

https://github.com/amungase/AJ-AI-PROJECTS
