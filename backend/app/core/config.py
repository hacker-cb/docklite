from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./docklite.db"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    
    # Projects
    PROJECTS_DIR: str = "/home/docklite/projects"
    DEPLOY_USER: str = "docklite"
    DEPLOY_HOST: str = "localhost"
    DEPLOY_PORT: int = 22
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    class Config:
        env_file = "../.env"
        case_sensitive = True


settings = Settings()

