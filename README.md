# ⚡ SET - Smart Expense Tracker with AI & Voice Intelligence

**SET (Smart Expense Tracker)** is an intelligent, full-stack financial analytics platform built with **Django**, **PostgreSQL**, **Scikit-Learn Machine Learning**, **Google Gemini AI**, and **Neural Voice Synthesis**. 

It enables users to ingest bank statements (PDF, CSV, Excel), automatically extracts and classifies transactions using machine learning, tracks cash/ATM expenditures, visualizes multi-account cashflows, and provides an interactive **Dual Voice + Chat AI Financial Assistant**.

---

## 🌟 Key Features

### 1. 📄 Multi-Format & Multi-Bank Statement Ingestion
- Ingest statements in **PDF**, **CSV**, and **Excel (`.xlsx`, `.xls`)** formats.
- Supports major Indian banks including **HDFC, SBI, ICICI, Axis, Kotak, and more**.
- **Smart Account Fingerprinting**: Automatically deduplicates and merges multi-month statements (e.g., three separate monthly PDFs for the same account merge cleanly into one single account ledger).

### 2. 🤖 Dual-Stage Machine Learning Pipeline
- **Bank Identification Model**: Scikit-Learn TF-IDF vectorizer + Calibrated LinearSVC to detect issuing bank from statement headers.
- **Transaction Categorizer**: Trained on thousands of real-world Indian transaction narrations (UPI, NEFT, IMPS, POS, ATM, Swiggy, Zomato, Amazon, Uber, IRCTC, etc.) into accurate spending categories (Food, Travel, Bills, Shopping, Investments, Salary, etc.).
- **Inline Learning**: Modify categories directly from the transaction ledger.

### 3. 🎙️ Real-Time Dual Voice & Chat AI Financial Assistant
- **Voice-First Experience**: Ask questions using the microphone; SET replies with both conversational text and natural voice audio.
- **SET Neural Voice Module**: Powered by high-definition neural speech (`en-IN-NeerjaNeural` / `en-IE-EmilyNeural` / Deepgram Aura).
- **Interactive Audio Controls**: Full playback controller bar with real-time waveform, **Pause in the middle**, **Resume/Continue from where you left off**, and **Stop**.
- **Gemini Powered Insights**: Connects to Google Gemini for deep financial insights, spending habits analysis, and intelligent Q&A with seamless offline rule-engine fallback.

### 4. 🏧 Unallocated Cash & ATM Spend Tracking
- Automatically detects ATM cash withdrawals.
- Prompts users to record petty cash expenses, vendor advances, or staff disbursements via a built-in modal to ensure 100% auditable accounting.

### 5. 📊 Interactive Analytics & Dashboard
- **Category Spend Distribution** (Interactive Doughnut Chart).
- **Top 5 Spending Categories** (Horizontal Bar Chart).
- **Monthly Income (Credit) vs Expense (Debit)** (Comparative Bar Chart).
- **Cumulative Net Flow Over Time** (Smooth Area Line Chart).
- Filter entire dashboard metrics by specific Bank / Account or view combined multi-account totals.

### 6. 📋 Transaction Ledger & Management
- Comprehensive transaction table with pagination, date formatting, and debit/credit color indicators.
- Filter by date range, specific account, transaction type, or category with a one-click **Reset Filters** button.
- Instant search by payee narration or description.

### 7. 👤 User Profile & Security Settings
- User signup, secure authentication, and session management.
- Update profile details (Name, Username, Email).
- Upload and display custom profile avatar.
- Secure password change and complete account deletion options.
- Polished, unified glassmorphism UI/UX across all pages.

---

## 🛠️ Tech Stack & Architecture

| Layer | Technologies |
|---|---|
| **Backend Framework** | Django 6.0, Python 3.12 |
| **Database** | PostgreSQL 16 (with automatic fallback to SQLite for local development) |
| **Machine Learning** | Scikit-Learn, Joblib, TF-IDF Vectorization, Calibrated LinearSVC |
| **AI LLM** | Google Gemini (Gemini Flash / Gemini Pro) via Google GenAI SDK |
| **Voice / Speech Engine** | Edge-TTS Neural Speech, Deepgram Aura API, Web Speech Recognition API |
| **Document Parsers** | `pdfplumber`, `pandas`, `openpyxl`, `python-dateutil` |
| **Frontend & UI** | Responsive Glassmorphism CSS, Chart.js, HTML5 Audio API |

---

## 📁 Project Structure

```text
SET/
├── accounts/               # Authentication, user profile, photo uploads, settings
├── ai_engine/              # Machine learning training, parser, bank detector & chat logic
│   ├── artifacts/          # Serialized scikit-learn models (category_model, bank_model)
│   ├── chat.py             # Financial chatbot & Gemini / local engine orchestration
│   ├── classifier.py       # Transaction category prediction
│   ├── bank_detector.py    # Statement bank header classification
│   ├── parser.py           # Robust PDF/CSV/Excel parser
│   └── train.py            # AI model training script
├── config/                 # Django project settings and root routing
├── sample_statements/      # Sample demo statements (HDFC, SBI, ICICI, etc.)
├── scripts/                # Synthetic statement generator and utility scripts
├── static/                 # Stylesheets (app.css), images, and client assets
├── templates/              # HTML templates
│   ├── accounts/           # Login, signup, profile settings
│   └── tracker/            # Home, upload, transactions ledger, dashboard
├── tracker/                # Core tracker app (views, models, migrations, TTS/Chat APIs)
├── manage.py               # Django CLI management script
└── requirements.txt        # Project dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.11+** installed
- **PostgreSQL 16** (optional, recommended for production; SQLite is used automatically as fallback)

### 2. Clone and Setup Environment

```powershell
# Navigate to project directory
cd SET

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# (Linux / macOS)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration

Create the database in PostgreSQL (if using PostgreSQL):

```sql
CREATE DATABASE smt_db;
```

Default connection settings (can be customized via environment variables):
- `POSTGRES_DB=smt_db`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=postgres`
- `POSTGRES_HOST=127.0.0.1`
- `POSTGRES_PORT=5432`

> **Note:** If PostgreSQL is not running or credentials differ, SET will automatically fall back to `db.sqlite3` seamlessly.

### 4. Train the ML Models & Run Migrations

```powershell
# Train the transaction & bank classification ML models
python manage.py train_ai

# Apply database migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Open your browser and visit: `http://127.0.0.1:8000/`

---

## 🧪 Demo Statements

Sample demo files for presentation and testing are available in the `sample_statements/` folder:
- `hdfc_sample.pdf`
- `sbi_sample.pdf`
- `icici_sample.csv`
- `multi_account_sample.xlsx`

To generate additional synthetic statements:
```powershell
python scripts\generate_sample_statements.py
```

Upload multiple statements simultaneously on the **Upload** page to see automatic multi-bank detection, statement deduplication, and combined dashboard visualizations.

---

## 🧠 Retraining AI Models

Whenever you update training narrations or add new bank statement formats:

```powershell
python manage.py train_ai
```

This compiles and saves two production models in `ai_engine/artifacts/`:
1. `category_model.joblib` — TF-IDF + Calibrated LinearSVC for transaction categories.
2. `bank_model.joblib` — Header signature classifier for bank accounts.

---

## 🔑 Environment Variables (Optional)

You can set these in your environment or a `.env` file:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key for advanced AI insights in the chatbot |
| `DEEPGRAM_API_KEY` | Deepgram API key for Aura ultra-low latency voice TTS |
| `POSTGRES_DB` | PostgreSQL database name (default: `smt_db`) |
| `POSTGRES_USER` | PostgreSQL user (default: `postgres`) |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_HOST` | Database host (default: `127.0.0.1`) |
| `POSTGRES_PORT` | Database port (default: `5432`) |
