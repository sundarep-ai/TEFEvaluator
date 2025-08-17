"""
TEF AI Practice Tool - Configuration Module
Centralized configuration management for the application
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Application Configuration
    app_name: str = "TEF AI Practice Tool"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Google Cloud Configuration
    google_cloud_project_id: Optional[str] = None
    google_cloud_location: Optional[str] = "us-central1"
    google_application_credentials: Optional[str] = None
    google_genai_use_vertexai: Optional[bool] = False
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database Configuration
    database_url: str = "sqlite:///./tef_evaluator.db"
    
    # Gemini API Configuration
    google_api_key: Optional[str] = None
    ai_model_name: str = "gemini-2.5-pro"  # Updated to match actual usage
    
    # CORS Configuration
    allowed_origins: List[str] = Field(alias="MY_ALLOWED_ORIGINS")
    
    # Timer Configuration
    writing_time_minutes: int = 60  # Writing practice time limit in minutes
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v):
        if v == "your-secret-key-change-this-in-production":
            raise ValueError("Please set a secure SECRET_KEY in production")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        try:
            if isinstance(v, str):
                # Handle comma-separated string from environment variable
                if v.strip():
                    return [origin.strip() for origin in v.split(",") if origin.strip()]
                else:
                    return ["http://localhost:3000", "http://localhost:8000"]
            elif isinstance(v, list):
                # Handle list input
                return v
            else:
                # Fallback to default
                return ["http://localhost:3000", "http://localhost:8000"]
        except Exception as e:
            # If any parsing fails, return default
            print(f"Warning: Failed to parse allowed_origins '{v}': {e}")
            return ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "production":
    settings.debug = False
    settings.allowed_origins = ["https://yourdomain.com"]  # Update for production
elif os.getenv("ENVIRONMENT") == "development":
    settings.debug = True
    settings.allowed_origins = ["http://localhost:3000", "http://localhost:8000"]

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "tef_evaluator.log",
            "mode": "a"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if settings.debug else "INFO",
            "propagate": False
        }
    }
}
