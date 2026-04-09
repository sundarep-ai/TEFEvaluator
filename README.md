<div align="center">
  <img src="https://img.shields.io/badge/L'Atelier-TEF%20Prep%20Studio-000666?style=flat-square">
  <br>
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&style=flat-square">
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-green?logo=fastapi&style=flat-square">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&style=flat-square">
  <img src="https://img.shields.io/badge/Vite-6-646CFF?logo=vite&style=flat-square">
  <img src="https://img.shields.io/badge/Tailwind%20CSS-3-38BDF8?logo=tailwindcss&style=flat-square">
  <img src="https://img.shields.io/badge/AI-Multi--Provider-orange?logo=openai&style=flat-square">
  <br><br>
  <h1>L'Atelier — TEF AI Practice Tool v1.3.0</h1>
  <p>A professional, responsive web application for practicing the <b>TEF Canada Writing</b> module,<br>powered by your choice of AI provider and built with React + Vite + Tailwind CSS.</p>
</div>

---

## Features

- **Authentication** — Secure login/registration with bcrypt password hashing and JWT tokens
- **Multi-Provider AI** — Bring your own API key: Google Gemini, OpenAI, Anthropic, or OpenRouter
- **AI Question Generation** — Generate authentic TEF Canada-style prompts for Task A and Task B
- **Smart Writing Interface** — 60-minute countdown timer, real-time word counters, clean editor
- **Advanced AI Evaluation** — Dual independent evaluators + judge consolidation for accurate scoring
- **Detailed Feedback** — Comprehensive analysis with error corrections and actionable recommendations
- **AI-Improved Answers** — Side-by-side comparison of your text vs. the AI-optimized version
- **Progress Dashboard** — Full submission history with scores, performance gauge, and detailed breakdowns
- **Dark/Light Theme** — Persistent theme preference with system-preference detection

---

## Tech Stack

| Layer      | Technology                                                                     |
|------------|--------------------------------------------------------------------------------|
| Backend    | Python 3.10+, FastAPI 0.111.0, google-genai / openai / anthropic SDKs        |
| Frontend   | React 18, Vite 6, Tailwind CSS 3                                              |
| Database   | SQLite with SQLAlchemy 2.0 ORM                                                 |
| Auth       | JWT (python-jose), bcrypt password hashing                                     |
| Icons      | Material Symbols Outlined                                                      |
| Fonts      | Manrope (headlines), Inter (body)                                             |

---

## AI Providers

The app supports four AI providers. Select your provider and paste your API key in the **Setup** page before starting a session — the key is stored only in your browser (localStorage) and never saved on the server.

| Provider      | Recommended Model      | Environment Variable    |
|---------------|------------------------|-------------------------|
| Google Gemini | `gemini-2.5-pro`       | `GOOGLE_API_KEY`        |
| OpenAI        | `gpt-4o`               | `OPENAI_API_KEY`        |
| Anthropic     | `claude-opus-4-6`      | `ANTHROPIC_API_KEY`     |
| OpenRouter    | `openai/gpt-4o`        | `OPENROUTER_API_KEY`    |

You can also set the key as an environment variable in `backend/.env` if you prefer a server-side default instead of entering it in the UI each time.

---

## Project Structure

```text
TEFEvaluator/
├── backend/                            # Python/FastAPI backend
│   ├── run.py                          # Main FastAPI server & all API endpoints
│   ├── ai_client.py                    # Unified AI client (Gemini / OpenAI / Anthropic / OpenRouter)
│   ├── config.py                       # Application settings
│   ├── model.py                        # Pydantic schemas & SQLAlchemy ORM models
│   ├── prompt_taskA.py                 # AI evaluation prompts for Task A
│   ├── prompt_taskB.py                 # AI evaluation prompts for Task B
│   ├── prompt_question_generation.py   # AI question generation prompts
│   ├── prompt_answer_generation.py     # AI answer improvement prompts
│   ├── requirements.txt                # Python dependencies
│   └── tests/
│       ├── test_script.py              # Standalone evaluation testing script
│       ├── test_sample.py              # Sample questions and test data
│       ├── test_prompts.ipynb          # Jupyter notebook for prompt testing
│       └── score_calibration.ipynb     # Score calibration analysis
│
├── frontend/                           # React + Vite frontend
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/
│   │   │   └── index.js               # API client (injects X-AI-* headers)
│   │   ├── components/
│   │   │   └── layout/
│   │   │       ├── AppLayout.jsx       # Main authenticated layout
│   │   │       ├── Sidebar.jsx         # Fixed left sidebar navigation
│   │   │       └── TopNav.jsx          # Fixed top navigation bar
│   │   ├── context/
│   │   │   ├── AuthContext.jsx         # Authentication state & actions
│   │   │   └── ThemeContext.jsx        # Dark/light theme management
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx           # Login & registration page
│   │   │   ├── DashboardPage.jsx       # Dashboard with stats & history
│   │   │   ├── SetupPage.jsx           # Practice session setup + AI provider config
│   │   │   ├── WritingPage.jsx         # Timed writing interface
│   │   │   └── ResultsPage.jsx         # AI feedback & score results
│   │   ├── App.jsx                     # Root component with router
│   │   ├── main.jsx                    # React entry point
│   │   └── index.css                   # Tailwind CSS directives
│   ├── index.html                      # Vite HTML entry point
│   ├── package.json
│   ├── vite.config.js                  # Vite config with API proxy
│   ├── tailwind.config.js              # Tailwind theme & colors
│   └── postcss.config.js
│
├── design/                             # Original UI design mockups
│   ├── login.html / login.png
│   ├── dashboard.html / dashboard.png
│   └── ai_feedback.html / ai_feedback.png
│
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- An API key from any supported provider (Google Gemini, OpenAI, Anthropic, or OpenRouter)

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env with your credentials
# (see Environment Variables section below)

# Run the backend
python run.py
# Backend starts at http://127.0.0.1:8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
# Frontend starts at http://localhost:5173
```

The Vite dev server proxies all `/api/*` requests to the FastAPI backend at `http://127.0.0.1:8000`.

---

## Environment Variables

Create a `.env` file in the `backend/` directory. Only `SECRET_KEY` is required; set whichever AI key matches your preferred provider.

```env
# JWT Secret — generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-secret-key-here

# AI provider keys — set the one(s) you want to use as server-side defaults.
# You can also enter your key directly in the Setup page UI instead.
GOOGLE_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENROUTER_API_KEY=your-openrouter-api-key

# Optional: set a server-side default provider (defaults to "google")
# AI_PROVIDER=openai
```

---

## API Endpoints

| Method | Endpoint                          | Auth | Purpose                                      |
|--------|-----------------------------------|------|----------------------------------------------|
| GET    | `/api/config`                     | No   | Frontend configuration                       |
| POST   | `/api/auth/register`              | No   | User registration                            |
| POST   | `/api/auth/login`                 | No   | User login, returns JWT                      |
| GET    | `/api/me`                         | Yes  | Current user info                            |
| GET    | `/api/submissions`                | Yes  | User's submission history                    |
| POST   | `/api/question`                   | Yes  | Generate Task A or B question via AI         |
| POST   | `/api/evaluate/task-a`            | Yes  | Evaluate Task A response                     |
| POST   | `/api/evaluate/task-b`            | Yes  | Evaluate Task B response                     |
| POST   | `/api/evaluate/both`              | Yes  | Evaluate both tasks, calculate final score   |
| POST   | `/api/generate-improved-answer`   | Yes  | Generate AI-improved version of answer       |

AI endpoints accept optional request headers to override the server default:

| Header          | Description                                         |
|-----------------|-----------------------------------------------------|
| `X-AI-Provider` | `google` \| `openai` \| `anthropic` \| `openrouter` |
| `X-AI-Key`      | Your API key for the chosen provider                |
| `X-AI-Model`    | Model name (e.g. `gpt-4o`, `claude-opus-4-6`)       |

---

## Database Schema

**Users**

| Column            | Type     | Description               |
|-------------------|----------|---------------------------|
| id                | INTEGER  | Primary key               |
| username          | VARCHAR  | Unique username           |
| hashed_password   | VARCHAR  | bcrypt hashed password    |
| created_at        | DATETIME | Account creation time     |

**Submissions**

| Column                     | Type     | Description                          |
|----------------------------|----------|--------------------------------------|
| id                         | INTEGER  | Primary key                          |
| user_id                    | INTEGER  | Foreign key → Users                  |
| task_a_question            | TEXT     | Task A prompt                        |
| task_a_response            | TEXT     | User's Task A response               |
| task_b_question            | TEXT     | Task B prompt                        |
| task_b_response            | TEXT     | User's Task B response               |
| rating_a / rating_b        | FLOAT    | Average AI rating (1–5)              |
| final_score                | INTEGER  | Final TEF score (150–700)            |
| justification_a/b          | TEXT     | AI analysis justification            |
| recommendation_a/b         | TEXT     | AI improvement recommendation        |
| originals_a/b              | JSON     | Error originals array                |
| corrections_a/b            | JSON     | Corrected versions array             |
| ai_improved_answer_taskA/B | TEXT     | AI-optimized version of response     |
| created_at                 | DATETIME | Submission timestamp                 |

---

## Evaluation System

1. **Dual Evaluators** — Two independent AI evaluations per task (encouraging + critical perspective)
2. **Score Consolidation** — Ratings averaged (50/50 weight), feedback merged
3. **Judge Pass** — Third AI call consolidates justifications and corrections into final feedback
4. **Final Score** — Exponential curve: `150 + ((normalized²) × 550)`, weighted 40% Task A + 60% Task B

---

## Scoring Scale

| Score Range | Level        | Label            |
|-------------|--------------|------------------|
| 600 – 700   | C2           | Excellence       |
| 500 – 600   | C1           | Avancé           |
| 400 – 500   | B2           | Intermédiaire+   |
| 150 – 400   | B1 and below | En progression   |

---

## Running Tests

```bash
cd backend

# Run evaluation test script
python tests/test_script.py

# Open Jupyter notebooks for analysis
jupyter notebook tests/test_prompts.ipynb
jupyter notebook tests/score_calibration.ipynb
```

---

<div align="center">
  <p>Multi-provider AI &nbsp;•&nbsp; © 2025 L'Atelier — Excellence en Français</p>
</div>
