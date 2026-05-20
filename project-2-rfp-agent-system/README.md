### 1. Recommended Repository Folder Structure

Before running git commands, verify that your local workspace folder (`rfp_agent_system`) is structured exactly like this:

```text
rfp_agent_system/
```markdown
# 🏢 Enterprise RFP Auto-Creation & Enhancement Dashboard (V2)

An enterprise-grade, high-leverage production pipeline that automatically converts unstructured client Request for Proposal (RFP) guidelines into highly tailored technical responses using a sequential multi-agent architecture.

## 🎯 Value Proposition & AI Leverage
- **Problem:** Manual RFP bid composition takes up to 20-40 hours across sales and legal engineering profiles.
- **Solution:** This framework processes raw documents via an assembly line of specialized agents, mapping real corporate capabilities accurately to client requirements in under 60 seconds without hallucinations.

## 🤖 Multi-Agent Architecture
- **Agent 1 (Procurement Auditor):** Parses incoming target client RFPs (`.pdf`, `.docx`, `.txt`), extracting raw technical demands and mandatory compliance frames.
- **Agent 2 (Solutions Architect Writer):** Automatically ingests the compliance checklist and aligns it directly against existing corporate past-performance records to generate a clean `.docx` response asset.

---

## 🛠️ Installation & Local Setup

### 1. Clone the Workspace Repository
```bash
https://github.com/amungase/AJ-AI-PROJECTS.git
cd to project directory
```

### 2. Build and Activate local Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

```

### 3. Install Pre-compiled Project Binaries

```bash
pip install -r requirements_v2.txt

```

---

## 🚀 How to Run (Secure CLI Mode)

To protect infrastructure privacy, this application relies on secure Command Line Interface environment parameters. Pass your Google AI Studio API key directly via the terminal execution string:

### On Windows Command Prompt (CMD):

```cmd
set GOOGLE_API_KEY=AIzaSyYourActualKeyHere
streamlit run app_v2.py

```

### On macOS / Linux Terminal:

```bash
export GOOGLE_API_KEY="AIzaSyYourActualKeyHere"
streamlit run app_v2.py

```

---

## 🧪 Testing instructions for Judges

Ready-to-use sample ingestion assets are stored in the `/sample_data` folder:

1. Ingest `ai_modernization_rfp_v2.txt` into the Client Target uploader module.
2. Ingest `my_company_capabilities_v2.pdf` into the Corporate Capabilities context module.
3. Click **"Trigger Multi-Agent Crew Pipeline"** to watch the data compile and export your formatted Word Document payload.

```

---

