"""Application settings.

Values can be overridden by environment variables (or backend/.env) using the
same names, upper-cased — e.g. `AI_PROVIDER=anthropic`, `PORT=9000`.

Secrets do NOT live here: SECRET_KEY and the provider API keys are read from the
environment in run.py / ai_client.py. This file is safe to commit, and is
tracked so a fresh clone can start the backend without hand-authoring it.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- App ---
    app_name: str = "L'Atelier — TEF Prep Studio"
    app_version: str = "2.0.0"

    # --- Server ---
    host: str = "127.0.0.1"
    port: int = 8000
    # The Vite dev server origin. Must be explicit: "*" is rejected by browsers
    # when allow_credentials=True.
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # --- Database ---
    database_url: str = "sqlite:///./tef.db"

    # --- Auth ---
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12

    # --- AI ---
    # Per-request X-AI-Provider / X-AI-Model headers override these.
    ai_provider: str = "google"
    # Fallback only, for a provider missing from ai_client.DEFAULT_MODELS.
    ai_model_pro: str = "gemini-3.6-flash"

    # --- Exam parameters (official TEF Canada expression écrite) ---
    writing_time_minutes: int = 60
    section_a_minutes: int = 25
    section_b_minutes: int = 35
    min_words_task_a: int = 80
    min_words_task_b: int = 200
    recommended_words_task_a: str = "80–120"
    recommended_words_task_b: str = "200–300"


settings = Settings()
