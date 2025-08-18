
<div align="center">
  <img src="https://img.shields.io/badge/TEF%20AI%20Practice%20Tool-Writing%20MVP-blueviolet?style=for-the-badge&logo=python" alt="TEF AI Practice Tool" height="32">
  <br>
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&style=flat-square">
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-green?logo=fastapi&style=flat-square">
  <img src="https://img.shields.io/badge/Bootstrap-5.3.3-purple?logo=bootstrap&style=flat-square">
  <img src="https://img.shields.io/badge/Gemini%20LLM-Vertex%20AI-orange?logo=googlecloud&style=flat-square">
  <br><br>
   <h1>📝 TEF AI Practice Tool v0.1.2</h1>
  <p>A professional, responsive web app for practicing the <b>TEF Canada Writing</b> module, powered by Google Gemini LLMs.<br><i>Fast, modern, and ready for your next exam.</i></p>
</div>


## 🚀 Features

<ul>
  <li><b>Authentication</b>: Login/registration with hashed passwords and JWT</li>
  <li><b>Dashboard</b>: See your historical submissions and scores</li>
  <li><b>Question Setup</b>: AI-generate or paste prompts for Task A and Task B</li>
  <li><b>Writing Interface</b>: 60-minute timer, live word counts</li>
  <li><b>Evaluation</b>: Dual evaluators + judge with structured outputs</li>
  <li><b>Results</b>: Final score out of 700, plus judge feedback per task</li>
  <li><b>Modern UI</b>: Clean, responsive Bootstrap 5</li>
</ul>

---

## 🛠️ Tech Stack

| Layer      | Technology                                    |
|------------|-----------------------------------------------|
| Backend    | Python, FastAPI, Google Gemini (Vertex AI)    |
| Frontend   | HTML5, Vanilla JS, Bootstrap 5                |
| Storage    | SQLite (SQLAlchemy ORM)                       |
| Auth       | JWT (python-jose), bcrypt (passlib)           |

---

## 📁 File Structure

```text
main.py           # FastAPI backend with auth, persistence, and evaluation endpoints
index.html        # Single-page Bootstrap UI with auth, practice, and dashboard
config.py         # App and AI model settings; auth configuration
model.py          # Pydantic schemas for evaluation and judge responses
prompt_taskA.py   # Prompt templates for Task A LLMs
prompt_taskB.py   # Prompt templates for Task B LLMs
requirements.txt  # All dependencies
.env              # Google Cloud auth for Vertex AI / Gemini
```

---

## ⚡ Quick Start

1. Install dependencies
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. Set up your .env (Vertex AI / Gemini)
   ```env
   GOOGLE_CLOUD_PROJECT_ID=your-gcp-project-id
   GOOGLE_CLOUD_LOCATION=your-gcp-region
   GOOGLE_APPLICATION_CREDENTIALS=your-service-account.json
   GOOGLE_GENAI_USE_VERTEXAI=True
   # Optional overrides
   # SECRET_KEY=your-secret
   # ACCESS_TOKEN_EXPIRE_MINUTES=120
   ```
3. Run the backend
   ```powershell
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Open index.html
   - Open in your browser. Login with the test account (testing/testing) or register a new one.

---

## 🧑‍💻 Usage (v0.1.2)

1. Login or register
2. Generate/paste prompts for Task A and B
3. Write responses; watch timer and word counts
4. Submit; Task A judge may appear first, then Task B; final score appears
5. Check Dashboard for historical submissions

Output shown:
- Judge’s justification and recommendation per task
- Original → Correction pairs (when provided by the judge)
- Final score out of 700

---

## 🔌 API Endpoints

- GET `/api/config` — Frontend config
- POST `/api/question` — Generate Task A or B prompt (auth required)
- POST `/api/evaluate/task-a` — Evaluate Task A (auth required)
- POST `/api/evaluate/task-b` — Evaluate Task B (auth required)
- POST `/api/evaluate/both` — Evaluate and persist both tasks (auth required)

New in v0.1.2:
- POST `/api/auth/register` — Register with username/password (hashed)
- POST `/api/auth/login` — Login to receive JWT
- GET `/api/me` — Current user info
- GET `/api/submissions` — List current user’s submissions

Notes:
- Use `Authorization: Bearer <token>` with authenticated routes.
- Passwords are hashed with bcrypt (passlib).
- Submissions are stored in `tef.db` (SQLite) with judge JSON and scores.
- Gemini responses are requested with structured schemas; only judge outputs are shown to end users.

---

## 🔐 Authentication

- JWT bearer token auth; tokens expire after a configurable duration (default 120 minutes).
- Test user is auto-created on startup: `testing` / `testing`.
- Config: see `config.py` (`secret_key`, `jwt_algorithm`, `access_token_expire_minutes`).

---

## 💾 Database

- SQLite file `tef.db` is created if absent.
- Tables:
  - `users(id, username, hashed_password, created_at)`
  - `submissions(id, user_id, task_a_question, task_a_response, task_b_question, task_b_response, rating_a, rating_b, final_score, judge_a JSON, judge_b JSON, created_at)`

---

## 📊 Dashboard

- After login, see your previous submissions with timestamps, scores, and prompts/responses.

---

## 📜 License

<img src="https://img.shields.io/github/license/yourusername/tef-ai-practice-tool?style=flat-square" alt="MIT License"> MIT
