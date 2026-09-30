# Smart Expense Tracker with AI based Categorizations (SMT)

MCA project: Django + PostgreSQL web app that reads bank statements (PDF, CSV, Excel and similar), extracts transactions with a trained AI pipeline, and shows overall plus per-account dashboards.

## What it does

1. Sign up / log in (old-money theme).
2. Home (wood theme) with three linked doors: **Upload → Transactions → Dashboard**.
3. Upload one or many statements. Same bank + holder + account (including split months as several PDFs) is merged. Different banks stay distinct.
4. Transactions page (mechanical theme) lists rows as extracted from the file, plus AI category.
5. Dashboard (treasury theme): combined analysis, or pick a bank / holder / account chip.
6. Any pipeline error returns to Home with the reason.

## Setup (Windows)

```powershell
cd $env:USERPROFILE\SMT
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

PostgreSQL 16 should be installed. Create the database once:

```sql
CREATE DATABASE smt_db;
```

Default connection (override with env vars if needed):

- `POSTGRES_DB=smt_db`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=postgres`
- `POSTGRES_HOST=127.0.0.1`
- `POSTGRES_PORT=5432`

If PostgreSQL is not running, the app **automatically uses SQLite** so you can still demo. After PostgreSQL is installed, restart the server; it will create `smt_db` when the default `postgres` user password is `postgres`.

Then:

```powershell
python -m ai_engine.train
python scripts\generate_sample_statements.py
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/accounts/signup/

Demo files are in `sample_statements\`. Upload several together (HDFC CSV + HDFC PDF + SBI PDF + ICICI CSV) to see multi-bank overall vs per-account dashboards.

## Train the AI again

```powershell
python manage.py train_ai
```

This retrains two scikit-learn models in `ai_engine/artifacts/`:

- **category_model.joblib** — TF-IDF + calibrated LinearSVC on transaction narrations (Food, Travel, Bills, …).
- **bank_model.joblib** — same architecture on statement headers (HDFC, SBI, ICICI, …).

Account identity also uses regex for account number and holder name, then a fingerprint so six months split across three PDFs still land on one account.

## Project layout

- `accounts/` login and signup
- `tracker/` upload, extract, dashboard
- `ai_engine/` dataset, training, PDF/CSV parser, classifier, bank identity
- `templates/` four visual themes
- `sample_statements/` viva demo files


