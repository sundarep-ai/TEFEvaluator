# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

L'Atelier — a TEF Canada writing-exam practice app. FastAPI backend (`backend/`) + React 18/Vite/Tailwind SPA (`frontend/`). The user brings their own AI provider API key; the backend is a thin orchestrator around a multi-call LLM evaluation pipeline. All user-facing UI copy is in French.

## Commands

```powershell
# Backend — must be run from backend/ (all imports are flat, e.g. `from model import ...`)
cd backend
python -m venv venv; venv\Scripts\activate
pip install -r requirements.txt
python run.py                      # uvicorn on settings.host:settings.port (127.0.0.1:8000), opens a browser tab

# Frontend
cd frontend
npm install
npm run dev                        # Vite on :5173, proxies /api/* -> 127.0.0.1:8000
```

There is no pytest suite, linter, or formatter configured. `backend/tests/test_script.py` is a **standalone Gemini-only script** (not a pytest test) that runs the full evaluation pipeline against the fixtures in `tests/test_sample.py` and prints scores — it makes real API calls. It needs both `backend/` and `backend/tests/` importable:

```powershell
cd backend
$env:PYTHONPATH="."; python tests/test_script.py
```

`tests/test_prompts.ipynb` and `tests/score_calibration.ipynb` are exploratory notebooks for prompt iteration and score-curve tuning.

## Files not in the repo (needed to run)

`.gitignore` excludes `config.py` and `*.json`, so two required files are absent and must be recreated locally:

- **`backend/config.py`** — must export a `settings` object with: `app_name`, `app_version`, `database_url`, `host`, `port`, `allowed_origins`, `jwt_algorithm`, `access_token_expire_minutes`, `ai_provider`, `ai_model_pro`, `writing_time_minutes`, `min_words_task_a`, `min_words_task_b`. (`pydantic-settings` is already a dependency.)
- **`frontend/package.json`** — deps in use: `react`, `react-dom`, `react-router-dom`, `vite`, `@vitejs/plugin-react`, `tailwindcss`, `postcss`, `autoprefixer`.

`backend/.env` supplies `SECRET_KEY` (read via `os.getenv`, not `settings`) plus optional server-side provider keys.

## Architecture

### Evaluation pipeline — 3 LLM calls per task, 6 per submission

Each task runs two *independent* evaluators with deliberately opposed personas (eval1 = encouraging, eval2 = critical), then a judge consolidates them:

1. **eval1 + eval2** → structured JSON scoring each metric 1–5 with justification, error `original`/`correction` arrays, and a recommendation. Metric lists are hardcoded as `metrics_taskA` / `metrics_taskB` in [run.py](backend/run.py) (8 criteria each) — they must match the Pydantic models `TEFTaskAResponse` / `TEFTaskBResponse` in [model.py](backend/model.py), the `CRITERION_LABELS` French display names, *and* the criteria enumerated in the prompt text, or metrics silently come back `None`. Two module-level `assert`s catch model/metric drift at import.
2. **`extract_feedback_summary`** averages the two evaluators 50/50 (this mean is the section `rating` — nothing downstream of it changes). **`merge_criteria`** separately keeps a per-criterion record (both evaluators' ratings, their mean, prose, error pairs) — persisted to `criteria_a` / `criteria_b` and rendered as the breakdown table in the UI. **`build_judge_input`** turns that per-criterion record into the judge's prompt input: justification/recommendation lines labelled by criterion, and originals/corrections as two number-paired lists — deliberately not a blind concatenation of both evaluators' prose, which left the judge summarizing an unlabeled wall of text with no way to tell which sentence was about which criterion.
3. **judge** call re-verifies the merged error corrections and produces the final English justification/recommendation stored in the DB.
4. **Final score**: see below.

### Scoring — one scale, 0–450

[scoring.py](backend/scoring.py) is the single source of truth. **Only the 0–450 scale is reported.** That is the attestation's *"équivalence ancien score"* column and the only one IRCC accepts; the /699 headline the attestation also carries is deliberately absent, because no authoritative rating→/699 mapping exists and a wrong number is worse than none. Do not reintroduce it.

`combined_rating` = `rating_a * 0.4 + rating_b * 0.6`, then `rating_to_score` interpolates linearly between anchors that are the **floors of the official IRCC NCLC bands** (2.0→181, 2.5→226, 3.0→271, 3.5→310, 4.0→349, 4.5→371, 4.75→393, 5.0→450). The consequence worth preserving: a half-point of rating maps onto exactly one NCLC level — a combined rating in [3.5, 4.0) is NCLC 7 and nothing else. NCLC 7 (310/450) is the Express Entry bar, so progress bars fill toward 310, not 450.

`score_report` returns `rating`, `score`, `scoreMax`, `nclc`, `cefr`, `bandFloor`/`bandCeiling`, `pointsToNextLevel`, `expressEntryEligible`, plus indicative per-section `sectionA` / `sectionB` breakdowns. The frontend mirrors the constants in [frontend/src/lib/score.js](frontend/src/lib/score.js) — update both.

`/api/evaluate/both` is the only evaluation route the frontend calls, and the only one that persists a `Submission`. `/api/evaluate/task-a` and `/api/evaluate/task-b` duplicate the same logic for single-task testing and write nothing.

### Multi-provider AI layer

`UnifiedAIClient` ([ai_client.py](backend/ai_client.py)) normalizes Google/OpenAI/Anthropic/OpenRouter behind `generate_text` and `generate_json`, always returning an `AIResponse` with a `.text` string. Only Google enforces the schema natively (`response_schema`); the others get the JSON Schema appended to the system prompt, so responses are parsed with `re.search(r"\{.*\}", ..., re.DOTALL)` everywhere. **Keep that regex-extraction contract intact** — any new provider must return raw text, not a parsed object.

Provider selection is per-request via the `get_ai_client` FastAPI dependency: `X-AI-Provider` / `X-AI-Key` / `X-AI-Model` headers → `AI_PROVIDER` env / `settings.ai_provider` → `DEFAULT_MODELS`. The frontend keeps the key in `localStorage` (`ai_provider`, `ai_api_key`, `ai_model`) and injects the headers in `apiPost` only ([api/index.js](frontend/src/api/index.js)) — so a GET route can never be AI-backed without changing `apiGet` too. Keys are never written to the server.

### Schema flattening

Gemini's `response_schema` rejects `$ref`/`$defs`/`allOf`, so `fully_flatten_pydantic_schema` (nested `CategoryFeedback` objects) and `flatten_pydantic_schema` (judge output) inline everything before the call. These two helpers are duplicated verbatim in `run.py` and `tests/test_script.py` — change both together.

### Prompts

`prompt_taskA.py` / `prompt_taskB.py` each export the same six names (`eval1_system_instruction_*`, `eval1_*_prompt`, `eval2_*`, `judge_*`); `prompt_answer_generation.py` follows the same convention. Templates are filled with `str.format()`, so any literal `{` or `}` added to prompt text must be doubled. Placeholders: evaluators use `{question}`/`{response}`/`{word_count}`, judge uses `{justification}`/`{recommendations}`/`{originals}`/`{corrections}`, improvement uses `{user_answer}`.

### Question bank

There is no AI question generation. `backend/questions_taskA.py` / `questions_taskB.py` each export a static list (`QUESTIONS_TASK_A` / `QUESTIONS_TASK_B`) of real/recalled TEF Canada prompts — sourced from published specimen and prep-site material (each entry carries its `source_url`) — wrapped in the exam's standard `Type de document` / `Objectif` / `Consignes` framing so the resulting `prompt` string is exactly the shape the evaluator prompts' `{question}` placeholder expects. `GET /api/questions` (no auth, not AI-backed) serves both lists verbatim; the frontend never calls an AI endpoint to get a question anymore.

### Frontend flow

`/practice` (SetupPage: configure provider, pick one Task A and one Task B question from the static bank) → `/practice/write` (WritingPage: 60-min timer, dual editors) → `/practice/results`. Questions, responses, and evaluation results are passed **only through react-router `location.state`**, not persisted client-side, so a page refresh mid-session bounces back to `/practice`. `AuthContext` holds the JWT in `localStorage` under `token`; `ThemeContext` drives Tailwind's `darkMode: 'class'`.

Note the duplication: `WRITING_TIME_MINUTES`, `MIN_WORDS_A`, `MIN_WORDS_B` are hardcoded in [WritingPage.jsx:5-7](frontend/src/pages/WritingPage.jsx#L5-L7) even though `/api/config` already serves them from `settings` — update both or wire the page to the endpoint.

Tailwind uses Material-3 design-token color names (`primary`, `on-surface-variant`, `surface-container-lowest`, …) defined in [tailwind.config.js](frontend/tailwind.config.js) for the light palette, with dark variants written inline as `dark:bg-slate-800`-style Tailwind defaults. `design/*.html` are the original static mockups the React pages were ported from — useful reference, not live code.

## Gotchas

- `get_current_user` parses the `Authorization: Bearer` header manually from `Request`; it is *not* an `OAuth2PasswordBearer` scheme, so FastAPI's docs UI won't show auth and the `token` query param is a legacy fallback.
- Startup seeds a `testing` / `testing` user into the DB ([run.py:146-158](backend/run.py#L146-L158)).
- `/api/generate-improved-answer` attaches its result to the user's *most recent* submission by `created_at` (tiebroken on `id`), not to a submission id.
- SQLite tables are created with `Base.metadata.create_all` and there are no migrations — adding a `Submission` column requires deleting the local `.db` file or altering it by hand.
- `submission_scores` recomputes the whole report from the stored `rating_a`/`rating_b` rather than reading the derived `score`/`nclc`/`cefr` columns back, so a calibration change in `scoring.py` applies to history instead of leaving mixed old and new numbers. The derived columns are still written on insert (`apply_scores`) so scores are queryable straight from SQLite.
- Every route that calls the AI is a plain `def`, not `async def` — the provider SDKs are synchronous and would block the event loop for the several minutes an evaluation takes. Keep new AI routes non-async.
