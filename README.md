# Packaged Commodity Compliance Scanner

An unfinished prototype. An inspector uploads photographs of a packaged commodity, the system reads
the labels, extracts the declarations, retrieves the relevant passages from the Legal Metrology
(Packaged Commodities) Rules, 2011, and asks a language model to evaluate them.

**Compliance judgement here comes from a language model, not from a deterministic rule engine.**
The output is an assessment to look at, not a determination to act on. There is no rule interpreter,
no versioned rule set, no audit trail, and no report.

---

## Flow

```
upload images → preprocess → OCR → LLM extracts declarations
             → normalize → retrieve rule passages → LLM evaluates
```

It runs as one synchronous request. `POST /inspections/{id}/process` calls `run_pipeline`, which
calls each step in order and returns the finished inspection. There is no graph, no background task
and no streaming.

If no LLM API key is configured the pipeline stops with a clear error and the inspection is marked
`FAILED`. There is no pattern-matching fallback.

---

## Structure

```
Backend/
  main.py  database.py  models.py  schemas.py  config.py
  seed_provisions.py            OCRs the rulebook into rule_passages
  routes/     auth_router.py  inspection_router.py
  services/   auth_service.py  inspection_service.py  storage_service.py
  pipeline/
    run.py                      the sequential pipeline
    llm.py                      model and embedding factory
    preprocessing/images.py     decode, resize, CLAHE
    extraction/ocr.py           PaddleOCR
    extraction/declarations.py  LLM structured extraction
    normalization/declarations.py
    compliance/retrieval.py     RAG over rule_passages
    compliance/evaluate.py      LLM evaluation
  legal/lmpc_2011.pdf
Frontend/src/
  pages/       Landing Login Register Dashboard Scan Inspection History
  components/  ImageUploader DeclarationList EvaluationView StatusBadge Navbar
  hooks/       useUser useInspection useImageUrls
  apis/api.ts  types/inspection.ts  index.css
```

---

## Database

Six tables.

| Table | Holds |
|---|---|
| `users` | id, username, password, full name |
| `inspections` | reference, owner, status, error, created at |
| `inspection_images` | storage path, filename, order, OCR text |
| `declarations` | one row per extracted field: field, value, confidence |
| `evaluations` | verdict plus the whole model output as one JSON column |
| `rule_passages` | rule reference, page, text, embedding for retrieval |

Findings are not modelled relationally. They live inside `evaluations.result`.

Status is `DRAFT`, `PROCESSING`, `COMPLETED` or `FAILED`.

Auth is a bearer token only, valid 12 hours. There is no refresh token.

---

## Running it

PaddleOCR needs **Python 3.12** — `paddlepaddle` publishes no wheel for 3.13 or 3.14.

```bash
cd Backend
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
cp .env.example .env          # then set LLM_API_KEY
.venv/Scripts/python.exe seed_provisions.py
.venv/Scripts/python.exe -m uvicorn main:app --reload
```

```bash
cd Frontend
npm install
cp .env.example .env.development
npm run dev
```

The first OCR call downloads about 16 MB of PP-OCR models into `~/.paddleocr`.

`seed_provisions.py` rasterises the rulebook and OCRs it, because the supplied PDF is a scan with no
text layer. Without it the retrieval table is empty and the evaluation has nothing to cite.

---

## Environment

`Backend/.env`

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres, or SQLite for a quick local run |
| `JWT_SECRET_KEY` | signs the access token |
| `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_BUCKET` | image storage; blank means local disk |
| `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL` | required; without a key processing fails |
| `EMBEDDING_MODEL` | embeddings for retrieval |
| `LEGAL_PDF_PATH` | the source notification |
| `ALLOWED_ORIGINS` | CORS origins |

`Frontend/.env.development` needs only `VITE_API_URL`.

`pgvector` is used only for `rule_passages`, and only on Postgres. On SQLite retrieval falls back to
keyword scoring.

---

## Known limitations

- The model decides compliance, so results vary between runs and are not reproducible.
- Retrieval passages come from OCR of a scan, so citation quality depends on how well the page read.
- Nothing verifies that a rule reference the model cites actually exists.
- No human review, no corrections, no audit trail. What the model extracts is what gets stored.
- No report generation.
- Requirements needing measurement or a registry lookup are only handled by asking the model to mark
  them `NOT_VERIFIABLE`. Nothing enforces that.
- Image upload only, no camera capture.
