<div align="center">
  <img src="https://img.shields.io/badge/L'Atelier-TEF%20Prep%20Studio-000666?style=flat-square">
  <br>
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&style=flat-square">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-green?logo=fastapi&style=flat-square">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&style=flat-square">
  <img src="https://img.shields.io/badge/Vite-6-646CFF?logo=vite&style=flat-square">
  <img src="https://img.shields.io/badge/Tailwind%20CSS-3-38BDF8?logo=tailwindcss&style=flat-square">
  <img src="https://img.shields.io/badge/AI-Multi--Provider-orange?logo=openai&style=flat-square">
  <br><br>
  <h1>L'Atelier — TEF AI Practice Tool v2.0.0</h1>
  <p>A web application for practising the <b>TEF Canada expression écrite</b> module,<br>powered by your choice of AI provider and built with React + Vite + Tailwind CSS.</p>
</div>

---

## Features

- **Authentication** — login/registration with bcrypt password hashing and JWT tokens
- **Multi-provider AI** — bring your own API key: Google Gemini, OpenAI, Anthropic, or OpenRouter
- **Curated question bank** — 45 Section A and 27 Section B real/recalled TEF Canada prompts to pick from
- **Timed writing interface** — 60-minute countdown with the official 25/35-minute section pacing, live word counters
- **Dual-evaluator scoring** — two independent evaluators plus a judge, mirroring the exam's two independent correctors
- **The score IRCC actually reads** — expression écrite out of 450 (the *"équivalence ancien score"* column) with its NCLC level and band, and nothing else to misread
- **Detailed feedback** — verified error corrections and actionable recommendations
- **AI-improved answers** — side-by-side comparison of your text vs. an optimised version
- **Progress dashboard** — submission history, performance gauge, and per-session breakdowns
- **Dark/light theme** — persistent preference with system detection

---

## Alignment with the official exam

The rubric mirrors the assessment criteria published by **Le français des affaires** for the TEF
expression écrite. Format confirmed unchanged since the 11 December 2023 revision.

| | Section A | Section B |
|---|---|---|
| Task | Continue a *fait divers* | Expose and defend a point of view |
| Time | 25 min | 35 min |
| Minimum | 80 words (80–120 expected) | 200 words (200–300 expected) |
| Weight | 40% (180/450 pts) | 60% (270/450 pts) |

Both sections are scored on the same eight criteria:

`task_fulfillment` · `content_relevance`/`argumentation` · `organization_coherence`/`structure` ·
`cohesion` · `vocabulary` · `grammar_syntax` · `spelling_punctuation` · `register_tone`

Two points where the exam is commonly misrepresented, and which this app follows:

- **Section B does not have to be a letter.** The official guidance is explicit
  (*"il n'est pas du tout obligatoire de rédiger son argumentation sous forme de lettre"*), and warns
  against long generic introductions and conclusions. Nothing here requires salutations, closing
  formulas, or a fixed Introduction/Argument I-II-III/Conclusion plan.
- **Section A must not recopy the opening.** Candidates must add new information of their own;
  recopying, summarising, or rephrasing the given text is penalised under `task_fulfillment`.

`spelling_punctuation` (*orthographe et ponctuation*) is scored separately from grammar, because the
official criteria list it separately.

---

## Scoring

### One scale: 0–450

The TEF attestation issued since the December 2023 revision shows a headline figure out of 699, but
**IRCC does not accept it.** Express Entry and every other federal stream read the *"Équivalence
ancien score"* column — expression écrite out of 450 — and that is the only column the official
NCLC/CLB equivalency table is written against. Entering the /699 number in an Express Entry profile
is a documented cause of refusal.

So this app reports **/450 and nothing else.** There is no second number on screen to misread. The
/699 figure is deliberately absent: no authoritative rating→/699 mapping exists (published charts
disagree with each other by 35+ points at the NCLC 7 boundary), and a wrong number there is worse
than no number.

NCLC equivalency for writing (official IRCC table, tests taken on or after 10 Dec 2023):

| NCLC  | Score /450  |
|-------|-------------|
| 10    | 393–450     |
| 9     | 371–392     |
| 8     | 349–370     |
| **7** | **310–348** |
| 6     | 271–309     |
| 5     | 226–270     |
| 4     | 181–225     |

**NCLC 7 (310/450) is the Express Entry writing threshold**, so progress bars in the app fill toward
310 rather than toward a perfect 450. IRCC stops at NCLC 10 — everything from 393 up earns the same
points — so the table does too.

### Rating → score

The 1–5 rating is interpolated linearly between anchors that are the **floors of the NCLC bands
above**: 2.0→181, 2.5→226, 3.0→271, 3.5→310, 4.0→349, 4.5→371, 4.75→393, 5.0→450. A half-point of
rating therefore maps onto exactly one NCLC level — a combined rating in [3.5, 4.0) is NCLC 7 and
nothing else. The steps compress above 4.5 because the real NCLC 9 and 10 bands are themselves
narrower (22 and 23 points wide, against 39 for NCLC 6).

> ### ⚠️ Calibration caveat
> The mapping from the 1–5 evaluator rating to a score is a **documented heuristic, not an official
> conversion** — Le français des affaires does not publish one, because human correctors score
> against level descriptors rather than a numeric mean. The anchors in
> [`backend/scoring.py`](backend/scoring.py) place the middle of the range LLM graders actually use
> (~3.5) on the NCLC 7 boundary. Read the **NCLC level** rather than the raw number: the level is what
> IRCC acts on, and it is the part this mapping is built to get right. Treat reported scores as
> **indicative practice feedback, not a prediction of your exam result**, and re-anchor against real
> attestation results before relying on them.

---

## Tech Stack

| Layer      | Technology                                                          |
|------------|---------------------------------------------------------------------|
| Backend    | Python 3.11+, FastAPI, google-genai / openai / anthropic SDKs        |
| Frontend   | React 18, Vite 6, Tailwind CSS 3                                    |
| Database   | SQLite with SQLAlchemy 2.0 ORM                                       |
| Auth       | JWT (python-jose ≥ 3.4), bcrypt password hashing                     |
| Icons      | Material Symbols Outlined                                            |
| Fonts      | Manrope (headlines), Inter (body)                                    |

---

## AI Providers

Select a provider and paste your API key on the **Setup** page before starting a session — the key is
stored only in your browser (`localStorage`) and is never saved on the server.

Defaults are the **newest low-cost tier** for each provider (verified August 2026). You can type any
model id you like into the Model field.

| Provider      | Default model         | Approx. cost /1M tok (in/out) | Environment variable |
|---------------|-----------------------|-------------------------------|----------------------|
| Google Gemini | `gemini-3.6-flash`    | $1.50 / $7.50                 | `GOOGLE_API_KEY`     |
| OpenAI        | `gpt-5.6-luna`        | $0.20 / $1.20                 | `OPENAI_API_KEY`     |
| Anthropic     | `claude-haiku-4-5`    | $1.00 / $5.00                 | `ANTHROPIC_API_KEY`  |
| OpenRouter    | `openai/gpt-5.6-luna` | passthrough + fee             | `OPENROUTER_API_KEY` |

A full evaluation is **6 model calls** (2 evaluators + 1 judge, per section), so cost per session is
roughly proportional to the rates above. Step up to a flagship model
(`gemini-3.1-pro`, `gpt-5.6-sol`, `claude-opus-5`) if you want the most reliable grading.

> **Retired model ids.** `gemini-2.5-pro`, `gpt-4o`, `openai/gpt-4o` and other pre-2026 ids are
> retired or retiring and return 404s. The Setup page automatically migrates a stored retired id to
> the current default for your provider.

**Schema enforcement per provider:** Google and OpenAI enforce the JSON schema natively; Anthropic
does too on models that support structured outputs, and falls back to a schema embedded in the system
prompt otherwise. OpenRouter uses JSON mode plus an embedded schema, because enforcement varies by the
upstream model it routes to.

---

## Project Structure

```text
TEFEvaluator/
├── backend/                            # Python/FastAPI backend
│   ├── run.py                          # FastAPI server, routes, evaluation pipeline
│   ├── ai_client.py                    # Unified AI client (Gemini / OpenAI / Anthropic / OpenRouter)
│   ├── scoring.py                      # TEF score scales + NCLC band mapping
│   ├── config.py                       # Application settings (no secrets)
│   ├── model.py                        # Pydantic schemas & SQLAlchemy ORM models
│   ├── prompt_taskA.py                 # Section A evaluation prompts
│   ├── prompt_taskB.py                 # Section B evaluation prompts
│   ├── questions_taskA.py               # Static bank of Section A prompts
│   ├── questions_taskB.py               # Static bank of Section B prompts
│   ├── prompt_answer_generation.py     # Answer improvement prompts
│   ├── requirements.txt                # Python dependencies
│   └── tests/
│       ├── test_script.py              # Standalone evaluation harness (real API calls)
│       ├── test_sample.py              # Sample questions and responses
│       ├── test_prompts.ipynb          # Prompt iteration notebook
│       └── score_calibration.ipynb     # Score curve analysis
│
├── frontend/                           # React + Vite frontend
│   ├── src/
│   │   ├── api/index.js                # API client (injects X-AI-* headers)
│   │   ├── lib/
│   │   │   ├── score.js                # Score/NCLC presentation helpers
│   │   │   └── text.js                 # Unicode-aware French word counting
│   │   ├── components/layout/          # AppLayout, Sidebar, TopNav
│   │   ├── context/                    # AuthContext, ThemeContext
│   │   ├── pages/                      # Login, Dashboard, Setup, Writing, Results
│   │   ├── App.jsx  main.jsx  index.css
│   ├── index.html  package.json  vite.config.js
│   ├── tailwind.config.js  postcss.config.js
│
├── design/                             # Original UI design mockups
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- An API key from any supported provider

### 1. Backend

```bash
cd backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Create .env — SECRET_KEY is required and the server refuses to start without it
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" > .env

python run.py
# Backend starts at http://127.0.0.1:8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# Frontend starts at http://localhost:5173
```

The Vite dev server proxies `/api/*` to the FastAPI backend at `http://127.0.0.1:8000`.

A `testing` / `testing` account is seeded on first startup.

---

## Environment Variables

Create `backend/.env`. Only `SECRET_KEY` is required; set whichever AI key matches your provider (or
enter it in the UI instead).

```env
# Required — the server refuses to start without it.
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-secret-key-here

# AI provider keys — server-side defaults. You can also enter your key in the Setup page.
GOOGLE_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENROUTER_API_KEY=your-openrouter-api-key

# Optional: server-side default provider (defaults to "google")
# AI_PROVIDER=openai
```

Non-secret settings (port, exam parameters, CORS origins) live in
[`backend/config.py`](backend/config.py) and can be overridden by environment variables of the same
name, e.g. `PORT=9000`.

---

## API Endpoints

| Method | Endpoint                          | Auth | Purpose                                        |
|--------|-----------------------------------|------|------------------------------------------------|
| GET    | `/api/config`                     | No   | Exam parameters, score scales, default models   |
| POST   | `/api/auth/register`              | No   | User registration                              |
| POST   | `/api/auth/login`                 | No   | User login, returns JWT                        |
| GET    | `/api/me`                         | Yes  | Current user info                              |
| GET    | `/api/submissions`                | Yes  | Submission history, each with a `scores` object |
| GET    | `/api/questions`                  | No   | Static bank of Section A/B prompts to pick from |
| POST   | `/api/evaluate/task-a`            | Yes  | Evaluate Section A only (not persisted)        |
| POST   | `/api/evaluate/task-b`            | Yes  | Evaluate Section B only (not persisted)        |
| POST   | `/api/evaluate/both`              | Yes  | Evaluate both sections, score, and persist     |
| POST   | `/api/generate-improved-answer`   | Yes  | Generate an improved version of an answer      |

AI endpoints accept optional headers to override the server default:

| Header          | Description                                         |
|-----------------|-----------------------------------------------------|
| `X-AI-Provider` | `google` \| `openai` \| `anthropic` \| `openrouter` |
| `X-AI-Key`      | Your API key for the chosen provider                |
| `X-AI-Model`    | Model id (e.g. `gemini-3.6-flash`)                  |

`/api/evaluate/both` returns a `scores` object:

```json
{
  "rating": 3.6, "score": 318, "scoreMax": 450,
  "nclc": 7, "cefr": "B2",
  "bandFloor": 310, "bandCeiling": 348, "pointsToNextLevel": 31,
  "expressEntryEligible": true, "expressEntryThreshold": 310,
  "sectionA": { "rating": 3.4, "score": 302, "nclc": 6, "cefr": "B1" },
  "sectionB": { "rating": 3.73, "score": 328, "nclc": 7, "cefr": "B2" }
}
```

Each of `taskA` / `taskB` also carries a `criteria` array — one entry per assessment criterion, with
its French label, the merged rating, both evaluators' individual ratings, prose and error pairs.

---

## Evaluation System

1. **Dual evaluators** — two independent evaluations per section, one encouraging and one demanding,
   mirroring the exam's two independent correctors
2. **Consolidation** — ratings averaged 50/50, prose and error lists merged. A per-criterion record is
   kept alongside the mean, so the results page can show which of the eight criteria cost the points
3. **Judge pass** — a third call verifies each correction is genuinely an improvement, drops false
   positives, merges duplicates, and produces the final feedback
4. **Final score** — sections weighted 40% A / 60% B, then mapped onto the 0–450 scale via the NCLC
   band anchors in `scoring.py`

---

## Database Schema

**Users** — `id`, `username`, `hashed_password`, `created_at`

**Submissions**

| Column                     | Type     | Description                          |
|----------------------------|----------|--------------------------------------|
| id                         | INTEGER  | Primary key                          |
| user_id                    | INTEGER  | Foreign key → Users                  |
| task_a/b_question          | TEXT     | Section prompts                      |
| task_a/b_response          | TEXT     | Candidate's responses                |
| rating_a / rating_b        | FLOAT    | Mean evaluator rating (1–5)          |
| combined_rating            | FLOAT    | 40% A + 60% B, 1–5                   |
| score                      | INTEGER  | Score /450 — the value IRCC wants    |
| nclc                       | INTEGER  | NCLC/CLB writing level, 0 if below 4 |
| cefr                       | TEXT     | Indicative CECRL band                |
| score_a / score_b          | INTEGER  | Indicative per-section score /450    |
| nclc_a / nclc_b            | INTEGER  | Indicative per-section NCLC          |
| criteria_a/b               | JSON     | Per-criterion ratings and feedback   |
| justification_a/b          | TEXT     | Judge's analysis                     |
| recommendation_a/b         | TEXT     | Judge's recommendation               |
| originals_a/b              | JSON     | Error excerpts                       |
| corrections_a/b            | JSON     | Corrections, index-aligned           |
| ai_improved_answer_taskA/B | TEXT     | AI-optimised version                 |
| created_at                 | DATETIME | Submission timestamp                 |

`rating_a` / `rating_b` are the source of truth: the full report is **recomputed from them at read
time**, so a change to the calibration curve applies to past submissions instead of leaving a mix of
old and new numbers in the history. The derived columns are written on insert anyway, so scores can be
queried straight from SQLite.

> There is no migration tooling — tables are created with `Base.metadata.create_all`. Adding a column
> means deleting the local `.db` file or altering it by hand.

---

## Running Tests

There is no pytest suite. `tests/test_script.py` is a standalone Gemini-only harness that runs the
full pipeline against the fixtures in `test_sample.py` and prints the scores. **It makes real, paid
API calls.** It needs both `backend/` and `backend/tests/` importable:

```powershell
cd backend
$env:PYTHONPATH="."; python tests/test_script.py     # PowerShell
```
```bash
cd backend
PYTHONPATH=. python tests/test_script.py             # bash
```

`tests/test_prompts.ipynb` and `tests/score_calibration.ipynb` are exploratory notebooks.

---

## Changelog — v2.0.0

**Exam alignment**
- Added the missing `spelling_punctuation` (*orthographe et ponctuation*) criterion to both sections
- Section B no longer requires a letter format, salutations, or a fixed argument plan
- Section A now penalises recopying or summarising the opening text
- Replaced Section B's meaningless *"maintains tone and style of given article"* criterion
- Fixed the Section B critical evaluator being told it was assessing Section A
- Aligned word-count guidance across prompts and UI; surfaced the 25/35-minute section pacing

**Scoring — now a single 0–450 scale**
- The app reports **one** number: expression écrite out of 450. That is the attestation's
  *"équivalence ancien score"* column and the only one IRCC accepts — entering the /699 headline in an
  Express Entry profile is a documented cause of refusal, so the UI no longer shows it at all
- Dropped the /699 figure entirely rather than guessing at it: published rating→/699 charts disagree
  with each other by 35+ points at the NCLC 7 boundary
- Rating→score anchors are now the floors of the official IRCC NCLC bands (181 / 226 / 271 / 310 /
  349 / 371 / 393), so a half-point of rating maps onto exactly one NCLC level — a combined rating in
  [3.5, 4.0) is NCLC 7 and nothing else
- Replaced the 150–700 curve, which matched no official scale and could exceed its own ceiling
- Pass threshold moved from an arbitrary ≥ 500 to NCLC 7 = 310/450; progress bars now fill toward
  310, not toward a perfect 450 that almost nobody needs
- Results show the NCLC band range (e.g. "NCLC 7 : 310–348") and points to the next level, so the
  number reads as the estimate it is
- Added indicative per-section scores, answering "which section is holding me back?"

**Feedback**
- Per-criterion breakdown is kept and displayed: each of the eight criteria now shows its merged
  rating and recommendation. Previously only the mean survived the pipeline, so the UI could say
  "3.4/5" but never which criterion cost the points

**Database** (no migration path — delete the local `.db` file)
- `final_score` replaced by `score` (/450), `combined_rating`, `nclc`, `cefr`
- Added `score_a` / `score_b` / `nclc_a` / `nclc_b` and `criteria_a` / `criteria_b`

**Correctness**
- Updated all four default model ids — the previous ones are retired
- Fixed crashes on `None` Gemini text, Anthropic thinking blocks and refusals, and unguarded judge
  JSON parsing
- Raised `max_tokens` 4096 → 16000 (evaluator JSON was being truncated)
- AI routes are no longer `async def`, so a running evaluation no longer blocks the whole server
- Fixed `created_at` being evaluated once at import (all rows shared one timestamp, so "most recent
  submission" was arbitrary — improved answers could attach to the wrong session)
- Fixed French word counting: `/\b\w+\b/` counted `"élève"` as two words and over-counted real prose
  by ~2×
- Sessions now survive a page refresh
- `SECRET_KEY` is validated at startup instead of failing at first login

**Dependencies**
- `python-jose` 3.3.0 → ≥ 3.4.0 (CVE-2024-33663, CVE-2024-33664)
- Removed unused `google-cloud-aiplatform`, `python-multipart`, `aiofiles`
- Added missing `pandas` / `matplotlib` / `numpy` and `tzdata`
- Restored `frontend/package.json` and `backend/config.py`, which a `*.json` / `config.py` gitignore
  rule had excluded from the repo

---

<div align="center">
  <p>Multi-provider AI &nbsp;•&nbsp; © 2026 L'Atelier — Excellence en Français</p>
</div>
