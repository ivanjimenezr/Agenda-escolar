"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # AI Integration
    gemini_api_key: str

    # Application
    environment: str = "development"
    debug: bool = True
    app_name: str = "Agenda Escolar Pro"
    api_version: str = "v1"

    # CORS (for frontend communication)
    # Add your production frontend URL here (e.g., https://yourapp.vercel.app)
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Parse CORS origins from comma-separated string.
        Returns list of allowed origins for CORS.
        """
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

        # In production, log the configured origins for debugging
        if self.is_production:
            print(f"[Config] Production CORS origins: {origins}")
            # If no origins configured in production, allow all temporarily
            if not origins:
                print("[Config] WARNING: No CORS_ORIGINS configured, allowing all origins")
                return ["*"]

        return origins if origins else ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


# Create global settings instance
settings = Settings()
