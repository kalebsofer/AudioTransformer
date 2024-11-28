import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BACKEND_URL: str
    TIMEOUT_SECONDS: int = 30

    if os.getenv("ENVIRONMENT") == "prod":
        POSTGRES_USER: str
        POSTGRES_PASSWORD: str
        POSTGRES_DB: str

    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'dev')}"


def get_settings() -> Settings:
    return Settings()
