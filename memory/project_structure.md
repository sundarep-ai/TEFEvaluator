---
name: TEFEvaluator project structure
description: Project has been restructured into backend/ and frontend/ folders as of 2026-04-08
type: project
---

Project restructured into separate backend/frontend architecture.

**Backend:** `backend/` — FastAPI + Python. Run from `backend/` directory with `python run.py`. Port 8000.

**Frontend:** `frontend/` — React 18 + Vite + Tailwind CSS. Run from `frontend/` with `npm run dev`. Port 5173. Proxies `/api/*` to backend.

**Why:** Clean separation of concerns. Backend serves only API (no more static files). Frontend is a proper React SPA.

**How to apply:** When working on backend code, look in `backend/`. When working on frontend UI, look in `frontend/src/`. The API contract is all `/api/*` routes defined in `backend/run.py`. The `/api/generate-improved-answer` endpoint was moved from root path to `/api/` prefix during this restructure.
