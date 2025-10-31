from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./docklite.db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    # Projects
    PROJECTS_DIR: str = "/home/docklite/projects"
    DEPLOY_USER: str = "docklite"
    DEPLOY_HOST: str = "localhost"
    DEPLOY_PORT: int = 22

    # Server
    HOSTNAME: Optional[str] = None  # If set, overrides system hostname

    # Traefik
    TRAEFIK_DASHBOARD_HOST: str = "localhost"  # Host for Traefik dashboard

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000


settings = Settings()
