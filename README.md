
<div align="center">
  <img src="https://img.shields.io/badge/TEF%20AI%20Practice%20Tool-Writin## 🧑‍💻 How to Use (v1.0.0)

### ## 🔌 API Endpoints

### Configuration
- `GET /api/config` — Application configuration and settings

### Authentication
- `POST /api/auth/register` — Create new user account
- `POST /api/auth/login` — Login and receive JWT token
- `GET /api/me` — Get current user information

### Questions & Practice
- `POST /api/question` — Generate AI-powered TEF questions (auth required)

### Evaluation
- `POST /api/evaluate/task-a` — Evaluate Task A response (auth required)
- `POST /api/evaluate/task-b` — Evaluate Task B response (auth required)
- `POST /api/evaluate/both` — Evaluate both tasks and save submission (auth required)

### User Data
- `GET /api/submissions` — Get user's submission history (auth required)

### Static Files
- `GET /styles.css` — Application stylesheets
- `GET /scripts.js` — Frontend JavaScript
- `GET /favicon.ico` — Application favicon

**Authentication**: All protected endpoints require `Authorization: Bearer <token>` header. **Login or Register**: Create an account or use the test account (`testing` / `testing`)
2. **Generate Questions**: Use AI to generate authentic TEF Canada prompts or paste your own
3. **Practice Writing**: Complete both Task A (narrative continuation) and Task B (opinion letter)
4. **Get AI Feedback**: Receive detailed evaluation with scores, corrections, and recommendations
5. **Track Progress**: Review your submission history and improvement over time

### Writing Tasks
- **Task A**: Continue a news article (80+ words, narrative style)
- **Task B**: Write an opinion letter (200+ words, formal argumentative style)
- **Timer**: 60-minute session with real-time countdown
- **Word Counter**: Live tracking for both tasks with minimum word requirements

### AI Evaluation System
- **Dual Evaluators**: Two independent AI evaluators assess your writing
- **Judge Consolidation**: A third AI judge provides final feedback and scoring
- **Comprehensive Metrics**: 
  - Task A: Task fulfillment, organization, content relevance, vocabulary, grammar, cohesion, style
  - Task B: Task fulfillment, structure, argumentation, vocabulary, grammar, cohesion, tone, style
- **Final Score**: Official TEF Canada scoring out of 700 pointslueviolet?style=for-the-badge&logo=python" alt="TEF AI Practice Tool" height="32">
  <br>
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&style=flat-square">
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-green?logo=fastapi&style=flat-square">
  <img src="https://img.shields.io/badge/Bootstrap-5.3.3-purple?logo=bootstrap&style=flat-square">
  <img src="https://img.shields.io/badge/Gemini%20LLM-2.5%20Pro/Flash-orange?logo=googlecloud&style=flat-square">
  <br><br>
   <h1>📝 TEF AI Practice Tool v1.0.0</h1>
  <p>A professional, responsive web app for practicing the <b>TEF Canada Writing</b> module, powered by Google Gemini 2.5 LLMs.<br><i>Fast, modern, and ready for your next exam.</i></p>
</div>


## 🚀 Features

<ul>
  <li><b>Authentication</b>: Secure login/registration with bcrypt password hashing and JWT tokens</li>
  <li><b>User Dashboard</b>: Complete submission history with scores, feedback, and performance tracking</li>
  <li><b>AI Question Generation</b>: Generate authentic TEF Canada-style prompts for both Task A and Task B</li>
  <li><b>Smart Writing Interface</b>: 60-minute timer, real-time word counts, and easy to write UI</li>
  <li><b>Advanced AI Evaluation</b>: Two independent AI evaluations, combined with a judge consolidation for accurate scoring</li>
  <li><b>Detailed Feedback</b>: Comprehensive analysis with error corrections and actionable improvement recommendations</li>
  <li><b>Dark/Light Theme</b>: Modern responsive UI with persistent theme preferences</li>
  <li><b>Complete TEF Scoring</b>: Final score out of 700 points following official TEF Canada methodology</li>
</ul>

---

## 🛠️ Tech Stack

| Layer      | Technology                                    |
|------------|-----------------------------------------------|
| Backend    | Python 3.10+, FastAPI 0.111.0, Google Gemini 2.5 (Pro/Flash) |
| Frontend   | HTML5, Vanilla JavaScript, Bootstrap 5.3.3   |
| Database   | SQLite with SQLAlchemy 2.0.23 ORM           |
| Auth       | JWT tokens (python-jose), bcrypt password hashing |
| AI Models  | Google Gemini 2.5 Pro/Flash via google-genai |
| Styling    | Custom CSS with Inter font, dark/light themes |

---

## 📁 Project Structure

```text
├── main.py                      # FastAPI backend with auth, evaluation endpoints, and database
├── index.html                   # Single-page application with responsive Bootstrap UI
├── scripts.js                   # Frontend JavaScript with theme support and API integration
├── styles.css                   # Custom CSS with dark/light theme variables
├── config.py                    # Application settings and configuration
├── model.py                     # Pydantic schemas and SQLAlchemy database models
├── prompt_taskA.py              # AI evaluation prompts for TEF Task A (narrative continuation)
├── prompt_taskB.py              # AI evaluation prompts for TEF Task B (opinion letter)
├── prompt_question_generation.py # AI prompts for generating TEF-style questions
├── requirements.txt             # Python dependencies
├── test_prompts.ipynb          # Jupyter notebook for testing AI evaluation system
├── test_sample.py              # Sample questions and responses for testing
├── test_script.py              # Standalone evaluation testing script
├── tef.db                      # SQLite database (auto-created)
├── favicon.ico                 # Application favicon
├── .env                        # Secret key and google cloud credentials (you have to create)
└── tefevaluator-*.json         # Google Cloud service account credentials (you have to create)
```

---

## ⚡ Quick Start

1. **Install dependencies**
   ```Command Prompt
   python -m pip install -r requirements.txt
   ```

2. **Set up Google Gemini API**
   - Create a `.env` file in the project root
   - Add your `.json` file in the project root
   - Add your Google API key:
   ```env
   GOOGLE_CLOUD_PROJECT_ID=your-google-cloud-project
   GOOGLE_CLOUD_LOCATION=your-google-cloud-location
   GOOGLE_APPLICATION_CREDENTIALS=your-google-service-account-json-filename
   GOOGLE_GENAI_USE_VERTEXAI=True

   SECRET_KEY=your-auto-generated-long-password
   ```

3. **Run the application**
   ```Command Prompt
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost:8000`
   - Register a new account and login to keep track of your progress
   - Start practicing your TEF Canada Writing skills!

> **Note**: The SQLite database (`tef.db`) will be created automatically on first run.

---

## 🧑‍💻 Usage (v1.0.0)

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

## 🔐 Authentication & Security

- **JWT Token Authentication**: Secure bearer token system with configurable expiration
- **Password Security**: Bcrypt hashing with salt for all user passwords
- **Session Management**: 120-minute token expiration (configurable)
- **Test Account**: Default `testing` / `testing` account created on startup
- **User Registration**: Secure new account creation with validation

**Configuration**: See `config.py` for customizing `secret_key`, `jwt_algorithm`, and `access_token_expire_minutes`.

---

## 💾 Database Schema

**SQLite Database**: `tef.db` (auto-created on first run)

### Tables

#### Users
```sql
users(
  id INTEGER PRIMARY KEY,
  username VARCHAR(64) UNIQUE,
  hashed_password VARCHAR(255),
  created_at DATETIME
)
```

#### Submissions
```sql
submissions(
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY,
  task_a_question TEXT,
  task_a_response TEXT,
  task_b_question TEXT,
  task_b_response TEXT,
  rating_a FLOAT,
  rating_b FLOAT,
  final_score INTEGER,
  judge_a JSON,
  judge_b JSON,
  justification_a TEXT,
  recommendation_a TEXT,
  originals_a JSON,
  corrections_a JSON,
  justification_b TEXT,
  recommendation_b TEXT,
  originals_b JSON,
  corrections_b JSON,
  created_at DATETIME
)
```

**Features**: Complete evaluation storage with AI feedback, error analysis, and scoring history.

---

## 📊 User Dashboard & Analytics

### Submission History
- **Complete Records**: View all past practice sessions with timestamps
- **Performance Tracking**: Monitor scores and improvement over time
- **Detailed Feedback**: Access AI evaluations, corrections, and recommendations
- **Score Breakdown**: See individual Task A and Task B ratings plus final score

### Features
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Search & Filter**: Find specific submissions quickly
- **Export Options**: Review detailed feedback for each submission
- **Progress Visualization**: Track your TEF Canada preparation journey

---

## 🧪 Testing & Development

### Test Files
- `test_prompts.ipynb`: Interactive Jupyter notebook for testing AI evaluation
- `test_script.py`: Standalone script for evaluation system testing
- `test_sample.py`: Sample questions and responses for development

### Development Commands
```powershell
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload

# Test the evaluation system
python test_script.py
```

---

## 🎨 UI/UX Features

### Modern Design
- **Bootstrap 5.3.3**: Professional, responsive component library
- **Inter Font**: Clean, readable typography optimized for screens
- **Custom CSS Variables**: Consistent color palette and spacing
- **Smooth Animations**: Enhanced user experience with CSS transitions

### Theme Support
- **Dark/Light Mode**: Toggle between themes with persistent storage
- **System Preference**: Automatically detects user's preferred color scheme
- **Accessibility**: High contrast ratios and screen reader support
- **Mobile Optimized**: Touch-friendly interface for all devices

---

## 📜 License

MIT License - feel free to use this project for your TEF Canada preparation!
