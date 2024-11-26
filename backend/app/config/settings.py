import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MINIO_URL: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_SECURE: bool = False

    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'dev')}"


def get_settings() -> Settings:
    return Settings()
