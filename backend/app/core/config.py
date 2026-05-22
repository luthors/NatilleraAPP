"""
Application settings loaded from environment variables.

All values can be overridden via a .env file or real environment variables.
See .env.example for the full list of required variables.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "Natillera API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "change-me-in-production-min-32-chars"

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://natillera:natillera@localhost:5432/natillera_db"
    DATABASE_URL_TEST: str = "sqlite:///./test.db"

    # ── JWT ───────────────────────────────────────────────────────────────────
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1

    # ── Security ─────────────────────────────────────────────────────────────
    BCRYPT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = (
        "http://localhost:3000,"
        "http://localhost:5173,"
        "http://localhost:19006"
    )

    # ── Email (SMTP) ──────────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "Natillera App"
    SMTP_FROM_EMAIL: str = "noreply@natillera.app"
    EMAILS_ENABLED: bool = False  # False en development para no enviar emails reales

    # ── File Storage ──────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 2

    # ── App URL (para links en emails y QR) ──────────────────────────────────
    APP_BASE_URL: str = "http://localhost:8000"
    FRONTEND_BASE_URL: str = "http://localhost:5173"

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def parse_origins(cls, v: str) -> str:
        return v

    def get_allowed_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
