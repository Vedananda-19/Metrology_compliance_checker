# PRISM — Legal Metrology Compliance Scanner

> Automated compliance checking for the **Legal Metrology (Packaged Commodities) Rules, 2011**.

PRISM turns a photograph of a packaged commodity into a legally-grounded compliance verdict. A field
officer uploads label images; the system reads the printed text, extracts the mandatory declarations,
and judges them against a **deterministic, versioned rule engine**. An officer verifies the findings
and generates a signed report; an inspector assigns cases and supervises officers.

**The model never decides compliance.** AI is used only to *read* and *structure* the label; the
pass / fail / not-verifiable verdict is produced solely by the rule engine, and every AI output is
grounded against the raw OCR text so nothing can be invented.

📄 **Full architecture & deployment:** [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)

---

## Highlights

- **Photo → verdict pipeline** — preprocess → OCR → extract → reconcile → normalize → rule engine.
- **Deterministic rule engine** — 63 versioned rules (`2026.09-draft1`) with three-valued logic; a
  requirement that can't be established from a photo is reported *not verifiable*, never "compliant".
- **Human-in-the-loop** — officers confirm/dismiss each finding; the original machine value is kept
  next to every correction for audit.
- **Two roles, one workflow** — officers capture & work a Kanban board; inspectors assign and oversee.
- **Signed reports** — per-inspection PDF/DOCX with the verdict, cited provisions, and Rule 7 font
  measurements.
- **Pluggable AI** — swap OCR/LLM providers (Google Gemini, OpenRouter, OpenAI) with a `.env` change.

---

## Tech stack

**Frontend** React 19 · TypeScript · Vite · React Query · React Router
**Backend** FastAPI · Pydantic v2 · SQLAlchemy 2.0 · Uvicorn
**Data** PostgreSQL + pgvector (SQLite for local dev) · Supabase Storage (local-disk fallback)
**AI** LangChain · vision-LLM OCR (or local PaddleOCR) · OpenCV for Rule 7 measurement
**Auth** JWT bearer · bcrypt

---

## Quick start (local)

Requires **Python 3.12** (pinned) and **Node 18+**.

### 1. Backend

```bash
cd Backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env        # then set JWT_SECRET_KEY and, for real AI, LLM_API_KEY
.venv/bin/python -m uvicorn main:app --reload
```

Runs at `http://localhost:8000` (`/health` to check). With `DATABASE_URL` unset it uses a local
SQLite file, so no database setup is needed to try it.

> **No AI key?** Everything starts and all non-AI screens work, but processing a package (OCR +
> extraction) needs a model. Add a Google Gemini or OpenRouter key to `LLM_API_KEY` to enable the
> real reading pipeline.

### 2. Frontend

```bash
cd Frontend
npm install
echo 'VITE_API_URL="http://localhost:8000"' > .env.development
npm run dev
```

Open `http://localhost:5173`.

### 3. (Optional) demo data

Seed realistic users and inspections — verdicts come from the real rule engine — to explore both
roles with populated dashboards:

```bash
cd Backend && .venv/bin/python seed_demo.py
```

Logins: `priya` (inspector), `rajesh` / `anita` (officers) — password `prism123`.

---

## Deployment

Backend and frontend deploy independently — the backend to any Linux host (`render.yaml` is included),
the frontend as static files to any CDN (`Frontend/vercel.json` handles SPA routing). See
[TECHNICAL_DOCUMENTATION.md § 12](TECHNICAL_DOCUMENTATION.md#12-deployment-framework) for the full
framework, environment matrix, and order of operations.

---

## Repository layout

```
Backend/     FastAPI app — routes · services · pipeline · engine · reports
Frontend/    React SPA — officer & inspector consoles
render.yaml  backend service definition
```

Full module-by-module map: [TECHNICAL_DOCUMENTATION.md § 10](TECHNICAL_DOCUMENTATION.md#10-repository-layout).

---

## Security

Secrets live only in the host environment (`.env` is gitignored). Rotate any key shared in plaintext.
Auth is a 12-hour JWT; authorization is enforced server-side per request. Details in
[TECHNICAL_DOCUMENTATION.md § 13](TECHNICAL_DOCUMENTATION.md#13-security).
