
<div align="center">
  <img src="https://img.shields.io/badge/TEF%20AI%20Practice%20Tool-Writing%20MVP-blueviolet?style=for-the-badge&logo=python" alt="TEF AI Practice Tool" height="32">
  <br>
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&style=flat-square">
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-green?logo=fastapi&style=flat-square">
  <img src="https://img.shields.io/badge/Bootstrap-5.3.3-purple?logo=bootstrap&style=flat-square">
  <img src="https://img.shields.io/badge/Gemini%20LLM-Vertex%20AI-orange?logo=googlecloud&style=flat-square">
  <br><br>
   <h1>📝 TEF AI Practice Tool v0.1.1</h1>
  <p>A professional, responsive web app for practicing the <b>TEF Canada Writing</b> module, powered by Google Gemini LLMs.<br><i>Fast, modern, and ready for your next exam.</i></p>
</div>


## 🚀 Features

<ul>
  <li><b>Start Screen</b>: Choose Writing Practice (future modules: Speaking, etc.)</li>
  <li><b>Question Setup</b>: Get an AI-generated writing prompt or enter your own for Task A and Task B (recommended)</li>
   <li><b>Writing Interface</b>: 60-minute timer, live word count, and text areas for both tasks
   <li><b>One-Click Submit</b>: A single Submit button (enabled only when both responses are filled)</li>
   <li><b>Evaluation Screen</b>: After submit, a dedicated screen shows loading; Task A judge feedback may appear first while Task B completes</li>
   <li><b>AI Evaluation</b>: Uses Gemini (via Vertex AI SDK) for two independent evaluations and a final judge consolidation</li>
   <li><b>Results Display</b>: A score out of 700, justification, recommendation, and an error analysis is provided</li>
  <li><b>Modern UI</b>: Clean, mobile-friendly design</li>
</ul>

---

## 🛠️ Tech Stack

| Layer      | Technology                                    |
|------------|-----------------------------------------------|
| Backend    | Python, FastAPI, Google Gemini (Vertex AI)    |
| Frontend   | HTML5, Vanilla JS, Bootstrap 5                |
| Config     | `.env` for secrets, `config.py` for settings  |

---

## 📁 File Structure

<details>
<summary>Click to expand</summary>

```text
main.py           # FastAPI backend, exposes endpoints for config, question generation, and evaluation
index.html        # Single-page Bootstrap UI, calls backend endpoints
config.py         # App and AI model settings
model.py          # Pydantic schemas for evaluation and judge responses
prompt_taskA.py   # Prompt templates for Task A LLMs
prompt_taskB.py   # Prompt templates for Task B LLMs
test_script.py    # Reference Gemini API logic (not used directly by the app)
requirements.txt  # All dependencies (FastAPI, google-genai, pandas, etc.)
.env              # Place your Google API key here as GOOGLE_API_KEY=...
```
</details>

---

## ⚡ Quick Start

1. <b>Install dependencies</b>
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. <b>Set up your <code>.env</code></b>
    - Copy <code>.env.example</code> if present, or create <code>.env</code> with the following required Google Cloud variables:
       ```env
       # Google Cloud Configuration (required for Gemini Vertex AI)
       GOOGLE_CLOUD_PROJECT_ID=your-gcp-project-id
       GOOGLE_CLOUD_LOCATION=your-gcp-region
       GOOGLE_APPLICATION_CREDENTIALS=your-service-account.json
       GOOGLE_GENAI_USE_VERTEXAI=True
       ```
3. <b>Run the backend</b>
   ```powershell
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
4. <b>Open <code>index.html</code></b>
   - For local dev, use a simple HTTP server (e.g. <code>python -m http.server</code>) or open directly in your browser if CORS is not an issue.

---

## 🧑‍💻 Usage (v0.1.1)

1. Start at the main screen, select <b>Writing Practice</b>
2. Generate or paste your Task A/B questions
3. Write your responses in both Task A (top) and Task B (bottom); track session timer and word counts
4. Click <b>Submit</b> (enabled once both responses are non-empty)
5. On the evaluation screen, Task A judge feedback may show first; once Task B completes, the <b>final score</b> appears

Output shown to the user:
- <b>Only the Judge LLM’s output</b> for each task, formatted as:
   - Justification (paragraph)
   - Recommendation (paragraph)
   - Originals → Corrections (bullet list)
- <b>Final score</b> computed out of 700

---

## 🧩 Extending

- Backend is modular for future Speaking module
- Prompts and schemas are in separate files for easy updates

---

## 🔌 API Endpoints

- GET `/api/config` — Frontend configuration (timers, version)
- POST `/api/question` — Generate Task A or B prompt (pass `{ "task": "A" | "B" }`)
- POST `/api/evaluate/task-a` — Evaluate Task A, returns `{ judge, rating }`
- POST `/api/evaluate/task-b` — Evaluate Task B, returns `{ judge, rating }`
- POST `/api/evaluate/both` — Evaluate both (returns judge outputs, ratings, and final score)

Notes:
- Backend calls Gemini with structured response schemas; only the judge outputs are surfaced to users.
- Final score is displayed when both task ratings are available.

## 📜 License

<img src="https://img.shields.io/github/license/yourusername/tef-ai-practice-tool?style=flat-square" alt="MIT License"> MIT
