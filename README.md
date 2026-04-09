<div align="center">
  <img src="https://img.shields.io/badge/L'Atelier-TEF%20Prep%20Studio-000666?style=flat-square">
  <br>
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&style=flat-square">
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-green?logo=fastapi&style=flat-square">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&style=flat-square">
  <img src="https://img.shields.io/badge/Vite-6-646CFF?logo=vite&style=flat-square">
  <img src="https://img.shields.io/badge/Tailwind%20CSS-3-38BDF8?logo=tailwindcss&style=flat-square">
  <img src="https://img.shields.io/badge/Gemini%20LLM-2.5%20Pro/Flash-orange?logo=googlecloud&style=flat-square">
  <br><br>
  <h1>L'Atelier — TEF AI Practice Tool v1.3.0</h1>
  <p>A professional, responsive web application for practicing the <b>TEF Canada Writing</b> module,<br>powered by Google Gemini 2.5 LLMs and built with React + Vite + Tailwind CSS.</p>
</div>

---

## Features

- **Authentication** — Secure login/registration with bcrypt password hashing and JWT tokens
- **AI Question Generation** — Generate authentic TEF Canada-style prompts for Task A and Task B
- **Smart Writing Interface** — 60-minute countdown timer, real-time word counters, clean editor
- **Advanced AI Evaluation** — Dual independent evaluators + judge consolidation for accurate scoring
- **Detailed Feedback** — Comprehensive analysis with error corrections and actionable recommendations
- **AI-Improved Answers** — Side-by-side comparison of your text vs. the AI-optimized version
- **Progress Dashboard** — Full submission history with scores, performance gauge, and detailed breakdowns
- **Dark/Light Theme** — Persistent theme preference with system-preference detection

---

## Tech Stack

| Layer      | Technology                                                    |
|------------|---------------------------------------------------------------|
| Backend    | Python 3.10+, FastAPI 0.111.0, Google Gemini 2.5 Pro/Flash  |
| Frontend   | React 18, Vite 6, Tailwind CSS 3                             |
| Database   | SQLite with SQLAlchemy 2.0.23 ORM                            |
| Auth       | JWT (python-jose), bcrypt password hashing                   |
| Icons      | Material Symbols Outlined                                     |
| Fonts      | Manrope (headlines), Inter (body)                            |

---

## Project Structure

```text
TEFEvaluator/
├── backend/                            # Python/FastAPI backend
│   ├── run.py                          # Main FastAPI server & all API endpoints
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
│   │   │   └── index.js               # API client functions
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
│   │   │   ├── SetupPage.jsx           # Practice session setup
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
- Google Cloud account with Gemini API access

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create a .env file)
cp ../.env.example .env
# Edit .env with your credentials

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

Create a `.env` file in the `backend/` directory:

```env
# Google Cloud / Gemini
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_GENAI_USE_VERTEXAI=True

# JWT Secret (generate a strong random key)
SECRET_KEY=your-secret-key-here
```

---

## API Endpoints

| Method | Endpoint                          | Auth | Purpose                                   |
|--------|-----------------------------------|------|-------------------------------------------|
| GET    | `/api/config`                     | No   | Frontend configuration                    |
| POST   | `/api/auth/register`              | No   | User registration                         |
| POST   | `/api/auth/login`                 | No   | User login, returns JWT                   |
| GET    | `/api/me`                         | Yes  | Current user info                         |
| GET    | `/api/submissions`                | Yes  | User's submission history                 |
| POST   | `/api/question`                   | Yes  | Generate Task A or B question via Gemini  |
| POST   | `/api/evaluate/task-a`            | Yes  | Evaluate Task A response                  |
| POST   | `/api/evaluate/task-b`            | Yes  | Evaluate Task B response                  |
| POST   | `/api/evaluate/both`              | Yes  | Evaluate both tasks, calculate final score |
| POST   | `/api/generate-improved-answer`   | Yes  | Generate AI-improved version of answer    |

---

## Database Schema

**Users**

| Column            | Type    | Description               |
|-------------------|---------|---------------------------|
| id                | INTEGER | Primary key               |
| username          | VARCHAR | Unique username            |
| hashed_password   | VARCHAR | bcrypt hashed password    |
| created_at        | DATETIME| Account creation time     |

**Submissions**

| Column                   | Type    | Description                          |
|--------------------------|---------|--------------------------------------|
| id                       | INTEGER | Primary key                          |
| user_id                  | INTEGER | Foreign key → Users                  |
| task_a_question          | TEXT    | Task A prompt                        |
| task_a_response          | TEXT    | User's Task A response               |
| task_b_question          | TEXT    | Task B prompt                        |
| task_b_response          | TEXT    | User's Task B response               |
| rating_a / rating_b      | FLOAT   | Average AI rating (1-5)              |
| final_score              | INTEGER | Final TEF score (150–700)            |
| justification_a/b        | TEXT    | AI analysis justification            |
| recommendation_a/b       | TEXT    | AI improvement recommendation        |
| originals_a/b            | JSON    | Error originals array                |
| corrections_a/b          | JSON    | Corrected versions array             |
| ai_improved_answer_taskA/B | TEXT  | AI-optimized version of response     |
| created_at               | DATETIME| Submission timestamp                 |

---

## Evaluation System

1. **Dual Evaluators** — Two independent Gemini 2.5 Pro evaluations per task (encouraging + critical)
2. **Score Consolidation** — Ratings averaged (50/50 weight), feedback merged
3. **Judge Pass** — Third Gemini call consolidates justifications and corrections
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
  <p>Powered by Google Gemini 2.5 Pro &nbsp;•&nbsp; © 2025 L'Atelier — Excellence en Français</p>
</div>
