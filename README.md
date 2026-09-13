# PRISM — Legal Metrology Compliance Scanner

Technical documentation: software architecture and deployment framework.

PRISM inspects photographs of a packaged commodity against the **Legal Metrology (Packaged
Commodities) Rules, 2011**. An officer uploads label images; the system reads the text, extracts the
mandatory declarations, and judges them against a deterministic rule engine. An officer then verifies
the findings and generates a signed compliance report.

**Design principle:** the language model never decides compliance. Extraction and phrasing use LLMs;
the pass/fail verdict is produced only by a deterministic, versioned rule engine. Every LLM output is
grounded against the OCR text so the model cannot invent a declaration.

---

## 1. Architecture overview

```
                 ┌─────────────────────────── Frontend (React SPA) ───────────────────────────┐
                 │  Officer: capture/upload, board, review, report                             │
                 │  Inspector: full repository, assignment, read-only boards                   │
                 └───────────────────────────────────┬─────────────────────────────────────────┘
                                                     │ HTTPS (JWT bearer)
                 ┌───────────────────────────────────▼─────────────────────────────────────────┐
                 │                         Backend (FastAPI)                                     │
                 │                                                                               │
                 │  routes ─ services ─ pipeline ─ engine ─ report                               │
                 │                                                                               │
                 │  Processing pipeline (one synchronous request):                               │
                 │                                                                               │
                 │   images → preprocess → OCR → extract → reconcile → normalize                 │
                 │                                         → rule engine → font measurement       │
                 │                                                                               │
                 └───────┬───────────────────┬────────────────────────┬──────────────────────────┘
                         │                   │                        │
                 ┌───────▼──────┐   ┌────────▼─────────┐   ┌──────────▼──────────┐
                 │ Postgres +   │   │ Supabase Storage │   │ OpenRouter (LLM)    │
                 │ pgvector     │   │ (label images)   │   │ gpt-4o-mini         │
                 │ (Supabase)   │   │                  │   │ PaddleOCR (local)   │
                 └──────────────┘   └──────────────────┘   └─────────────────────┘
```

### Processing pipeline

`POST /inspections/{id}/process` runs the whole pipeline synchronously in `pipeline/run.py`:

| Stage | Module | What it does |
|---|---|---|
| Preprocess | `preprocessing/images.py` | Decode, resize to 1600 px, CLAHE contrast (OpenCV) |
| OCR | `extraction/ocr.py` | **PaddleOCR** (local, no cloud) reads text and per-word boxes |
| Extract | `extraction/declarations.py` | LLM pulls the label into a typed `PackageDeclarations` schema |
| Reconcile | `extraction/inference.py` | A second LLM pass re-files fields into the right slots; every value is grounded against the OCR text and range-checked, so nothing is invented |
| Normalize | `normalization/declarations.py` | Flattens declarations to engine fact paths and builds context facts |
| Evaluate | `compliance/evaluate.py` + `engine/` | The **deterministic rule engine** produces the verdict |
| Measure | `measurement/` | ArUco reference marker → physical scale → Rule 7 character height in mm |

### Rule engine

`engine/engine.py` interprets a versioned rule set (`engine/rules/lmpc_2011_rules.json`, 63 rules) with
**three-valued logic** — `TRUE` / `FALSE` / `UNKNOWN`. Each rule carries `applies_when`, `exempt_when`,
a `check`, a `verification_mode`, and a `severity`. A requirement that cannot be established from a
photograph is reported `NOT_VERIFIABLE`, never silently marked compliant. Numeric checks derive a
canonical `base_value` from the parsed value and unit; format and wording checks read the declaration
text. The engine, not the model, is the sole authority on the verdict.

### LLM layer

`pipeline/llm.py` is a provider-agnostic factory. All three generative steps — extraction,
reconciliation, and report justification — run on **OpenRouter** (`gpt-4o-mini`) using OpenAI
structured outputs (`json_schema`) with retry-on-empty. Google Gemini is retained only for the
embedding model used when seeding rule passages. Swapping providers is a change to `.env`, not code.

### Font measurement (Rule 7)

`measurement/reference.py` detects an ArUco marker of a user-supplied physical size and computes
`mm_per_pixel` from its corners. `measurement/font.py` locates each declaration in the OCR word boxes,
segments the printed characters with OpenCV, and converts height to millimetres, then checks it against
the Rule 7 minimum for the panel area. Unreliable measurements return `UNABLE_TO_VERIFY` rather than a
guess.

### Reports

`services/report/` builds a per-inspection compliance report in **PDF** (reportlab) and **DOCX**
(python-docx). It is generated only after an officer finalises verification. It contains the
compliant/non-compliant/not-verifiable counts, officer details, each confirmed violation with a
grounded plain-language justification and the official rule text, the not-verifiable findings, and the
Rule 7 character-height measurements.

### Roles and workflow

Two roles drive a Kanban workflow (`ASSIGNED → IN_PROGRESS → ACTION_REQUIRED → RESOLVED`):

- **Officer** — field worker. Captures/uploads images, processes, reviews each violation, finalises,
  and downloads the report. Processing auto-advances a case from `ASSIGNED` to `IN_PROGRESS`.
- **Inspector** — supervisor. Sees every case, assigns cases to officers, and views officer boards
  read-only.

---

## 2. Technology stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript, Vite, React Query, plain CSS |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2.0 |
| Database | PostgreSQL + pgvector (Supabase) |
| Object storage | Supabase Storage via REST (httpx); local disk fallback |
| OCR | PaddleOCR + paddlepaddle (local, CPU) |
| Vision | OpenCV (preprocessing, ArUco, character segmentation) |
| LLM | OpenRouter (`gpt-4o-mini`) via LangChain; Google Gemini for embeddings |
| Auth | JWT bearer (python-jose), bcrypt password hashing (passlib) |
| Reports | reportlab (PDF), python-docx (DOCX) |

---

## 3. Repository layout

```
backend/
  main.py  database.py  models.py  schemas.py  config.py
  seed_provisions.py                  OCRs the rulebook into rule_passages
  routes/       auth_router.py  inspection_router.py  rule_router.py
  services/     auth_service.py  inspection_service.py  storage_service.py
                report/           report assembler, PDF + DOCX builders, rules digest
  pipeline/
    run.py                            the sequential pipeline
    llm.py                            provider-agnostic model + embedding factory
    preprocessing/images.py           decode, resize, CLAHE, blur check
    extraction/ocr.py                 PaddleOCR text + word boxes
    extraction/declarations.py        LLM structured extraction
    extraction/inference.py           second-pass reconciliation, grounded
    normalization/declarations.py     declarations → engine facts
    compliance/evaluate.py            runs the engine, shapes findings
    measurement/reference.py          ArUco scale
    measurement/font.py               character height + Rule 7 check
  engine/
    engine.py                         deterministic rule interpreter
    rules/lmpc_2011_rules.json        63 versioned rules
    rules/reference_tables.json       Rule 7 tables, unit tables
frontend/
  src/
    pages/        Officer + Inspector dashboards, Inspection, Rules, History, auth
    components/   KanbanBoard, EvaluationView, DeclarationList, CameraCapture, …
    hooks/        useUser, useInspection, useTheme
    apis/api.ts   axios client (JWT interceptor)
    types/inspection.ts   index.css
```

---

## 4. Data model

Postgres tables (created on startup via `Base.metadata.create_all`):

| Table | Holds |
|---|---|
| `users` | id, username, password hash, full name, `role` |
| `inspections` | reference, owner, `assigned_to`, `status`, `stage`, verification state |
| `inspection_images` | Supabase storage path, filename, order |
| `ocr_texts` | raw OCR text per image |
| `declarations` | one row per extracted field: field path, value, confidence |
| `evaluations` | verdict + full engine result as one JSON column |
| `finding_reviews` | officer decision + note per rule |
| `font_measurements` | measured height, scale, status per declaration |
| `rule_passages` | rule text + `vector(3072)` embedding for retrieval |

Auth is a bearer token valid 12 hours; there is no refresh token.

---

## 5. Deployment framework

The two apps deploy independently: the backend to any Linux host that can run a Python process, the
frontend to a static host such as Vercel.

### 5.1 Backend

Requires **Python 3.12** — `paddlepaddle` publishes no wheel for 3.13+.

Environment (set on the host, never in the repo):

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection (Supabase pooler) |
| `JWT_SECRET_KEY` | signs access tokens |
| `SUPABASE_URL` / `SUPABASE_KEY` / `SUPABASE_BUCKET` | image storage (blank = local disk) |
| `LLM_PROVIDER` / `LLM_API_KEY` / `LLM_MODEL` | generative model (`openrouter`, `openai/gpt-4o-mini`) |
| `INFERENCE_PROVIDER` / `INFERENCE_API_KEY` / `INFERENCE_MODEL` | reconciliation + justification model |
| `LLM_BASE_URL` | OpenRouter base URL |
| `GOOGLE_EMBED_KEY` / `EMBEDDING_MODEL` | embeddings for rule-passage seeding |
| `OCR_LANG` | PaddleOCR language (`en`, `devanagari`, …) |
| `ALLOWED_ORIGINS` | comma-separated CORS origins (the frontend URL) |

Build and run:

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

```bash
python -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```

Run from inside `backend/`. Tables are created on startup and the rule passages are already seeded, so
no migration step is required. Keep `--workers` low: PaddleOCR loads its model into each worker.
PaddleOCR downloads ~16 MB of models on the first request into a writable cache (`~/.paddleocr`), so
give the host a persistent filesystem and warm it with one request after deploy.

### 5.2 Frontend

`VITE_API_URL` is baked in at build time and must point at the deployed backend:

```bash
echo 'VITE_API_URL="https://your-backend-domain"' > .env.production
```

```bash
npm ci && npm run build
```

Deploy the resulting `dist/` as static files. It is a single-page app, so configure the host to fall
back to `index.html` for unknown routes.

### 5.3 Order of operations

1. Deploy the backend; note its public URL.
2. Set `ALLOWED_ORIGINS` on the backend to the frontend URL and restart.
3. Set `VITE_API_URL` to the backend URL, `npm run build`, and deploy `dist/`.

---

## 6. Local development

Backend:

```bash
cd backend
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
cp .env.example .env          # then set the keys
.venv/Scripts/python.exe -m uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
npm install
echo 'VITE_API_URL="http://localhost:8000"' > .env.development
npm run dev
```

---

## 7. Security notes

- `.env` is gitignored and must stay so. Provide all keys through the host environment.
- Rotate any key that has been shared in plain text; treat shared keys as compromised.
- The frontend stores the JWT in `localStorage`; a 401 clears it and returns to sign-in.
