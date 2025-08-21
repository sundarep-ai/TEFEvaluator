from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    app_name: str = "TEF AI Practice Tool"
    app_version: str = "1.2.0"
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True

    # UI/Practice
    writing_time_minutes: int = 60
    min_words_task_a: int = 80
    min_words_task_b: int = 200

    # CORS
    allowed_origins: List[str] = ["*"]

    # AI
    # We rely on google-genai to read GOOGLE_API_KEY from the environment (.env)
    ai_model_fast: str = "gemini-2.5-flash"
    ai_model_pro: str = "gemini-2.5-pro"

    database_url: str = "sqlite:///./tef.db"

    # Auth / Security
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120


settings = Settings()
