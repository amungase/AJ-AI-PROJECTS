# 🏦 CASA Multi-Agent Corporate Onboarding & Compliance Engine

An enterprise-grade corporate onboarding engine that automates multi-page bank document auditing, extracting structural metadata and dynamically detecting compliance violations or missing signatures through sequential AI agents.

---

## 🚀 System Architecture & Overview
This platform replaces the slow, error-prone manual review of complex business applications with an automated, sequential multi-agent workforce orchestrated via **CrewAI** and powered by **Gemini 2.5 Flash**:

1. **Intelligent Ingestion:** Accepts corporate text, PDF deeds, or document packages through an interactive interface with Human-in-the-Loop override options.
2. **Context Enrichment:** Automatically vectorizes incoming data and queries a **Pinecone Vector Database** to retrieve active regional regulatory policies and tax frameworks.
3. **Sequential Multi-Agent Analysis:**
   * **Agent A (The Fact Miner):** Extracts structural metadata like legal entity names, ID registries, and UBOs holding >25% control shares.
   * **Agent B (The Legal Auditor):** Cross-examine those extracted elements against the live legal snippets queried from the Vector DB.
4. **Visual "Missing Signature" Verification:** Uses Gemini's multimodal vision features to analyze closing signature blocks. If an execution line or corporate seal area is left as blank white space, it trips a custom logic gate—halting the pipeline with a `VERIFICATION_HOLD` error status.

---

## 🛠️ Tech Stack & AI Toolkit
* **Orchestration Framework:** `CrewAI`
* **Core LLM & Vision Engine:** `Gemini 2.5 Flash`
* **Vector Database:** `Pinecone`
* **User Interface:** `Streamlit Dashboard UI`

---

## 💻 Step-by-Step Local Setup Instructions

Follow these exact steps to clone, configure, and launch the application dashboard locally:

### 1. Clone the Repository
```bash
git clone [https://github.com/amungase/casa-onboarding-ai.git](https://github.com/amungase/casa-onboarding-ai.git)
cd casa-onboarding-ai

```

### 2. Set Up a Virtual Environment (Isolated Environment)

```bash
python -m venv venv

# On Windows Command Prompt:
venv\Scripts\activate

# On macOS / Linux:
source venv/bin/activate

```

### 3. Install Required Dependencies

```bash
pip install -r requirements.txt

```

### 4. Configure Environment Keys (`.env`)

The engine expects environment variables to communicate with your AI services.
Create a brand new file named `.env` in the root folder of your project and paste the following, replacing the placeholders with your actual keys:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
PINECONE_API_KEY=your_actual_pinecone_api_key_here

```

*(Note: Your `.env` file is protected locally and will not be pushed to public GitHub history thanks to your `.gitignore` configuration.)*

### 5. Launch the Dashboard Interface

Run your main interface file using Streamlit to boot the local web application:

```bash
streamlit run app.py

```

*(Note: If your main frontend script is named something other than `app.py`, change `app.py` to match your exact file name.)*

---

## 🔗 Portfolio Integration

This project is an active component of my professional portfolio workspace. You can explore my other engineering builds here:
👉 https://ajgenstudio.lovable.app/
