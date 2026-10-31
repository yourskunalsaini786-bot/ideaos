"""Application configuration using Pydantic Settings."""
import os
from functools import lru_cache
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "apps/api/.env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "IdeaOS API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./ideaos.db",
        description="Database connection URL (PostgreSQL asyncpg or SQLite aiosqlite)",
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 5

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Ensure async driver is used for postgresql URLs."""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v

    # Redis
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    # Supabase (optional for local dev)
    SUPABASE_URL: Optional[str] = "http://localhost:54321"
    SUPABASE_SERVICE_KEY: Optional[str] = "dev-service-role-key"
    SUPABASE_JWT_SECRET: Optional[str] = "dev-jwt-secret-at-least-32-chars-long"
    SUPABASE_ANON_KEY: Optional[str] = "dev-anon-key"

    # Authentication (Clerk)
    CLERK_PUBLISHABLE_KEY: Optional[str] = "pk_test_dev"
    CLERK_SECRET_KEY: Optional[str] = "sk_test_dev"
    CLERK_WEBHOOK_SECRET: Optional[str] = None

    # AI Providers (Google Gemini as default)
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API key")
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_MODEL_REASONING: str = "gemini-2.5-pro"

    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL_REASONING: str = "claude-opus-5-5"
    ANTHROPIC_MODEL_BALANCED: str = "claude-sonnet-5-5"
    ANTHROPIC_MODEL_FAST: str = "claude-haiku-5-5"

    OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_PROVIDER: str = "gemini"
    EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIMENSIONS: int = 768

    # Transcription
    STT_PROVIDER: str = "gemini"  # gemini native multimodal or whisper
    WHISPERX_API_URL: Optional[str] = None
    WHISPERX_API_KEY: Optional[str] = None

    # Storage (Local or Cloudflare R2)
    STORAGE_BACKEND: str = "local"  # "local" or "r2"
    LOCAL_STORAGE_DIR: str = "./uploads"
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET: str = "ideaos-assets"
    R2_PUBLIC_URL: Optional[str] = None

    # Temporal
    TEMPORAL_ADDRESS: str = "localhost:7233"
    TEMPORAL_NAMESPACE: str = "default"
    TEMPORAL_API_KEY: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: Optional[str] = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: Optional[str] = "redis://localhost:6379/2"

    # Security
    SECRET_KEY: str = Field(
        default="ideaos-insecure-dev-secret-key-32-chars-min!",
        description="Secret key for signing",
    )
    ENCRYPTION_KEY: str = Field(
        default="ideaos-insecure-encryption-key-32ch!",
        description="Encryption key for sensitive data",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # File Upload
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_MIME_TYPES: list[str] = [
        "audio/mpeg", "audio/wav", "audio/mp4", "audio/m4a", "audio/webm", "audio/ogg",
        "video/mp4", "video/webm", "video/quicktime",
        "image/jpeg", "image/png", "image/webp", "image/gif",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain", "text/markdown",
    ]

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "*"]

    # Webhooks
    WEBHOOK_SECRET: Optional[str] = None

    # Feature Flags
    ENABLE_FUSION_ENGINE: bool = True
    ENABLE_BRAND_GUARDIAN: bool = True
    ENABLE_CALENDAR: bool = True
    ENABLE_ANALYTICS: bool = True


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
