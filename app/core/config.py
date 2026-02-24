from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings class to load configuration from environment variables and .env file.
    """

    APP_NAME: str = "FastAPI"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_DATABASE: str = "test"
    DB_USERNAME: str = "root"
    DB_PASSWORD: str = "password"

    MAIL_HOST: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = "your_email@gmail.com"
    MAIL_PASSWORD: str = "your_app_password"
    MAIL_TLS: bool = True
    MAIL_FROM: str = "your_email@gmail.com"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    LOGGER_ROTATION: str = "10 MB"
    OTP_LENGTH: int = 6
    OTP_EXPIRE: int = 10

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5
    ALLOWED_TYPES: list = ["image/jpeg", "image/png"]

    SECRET_KEY: str = "secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE: int = 10

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, env_file_encoding="utf-8"
    )

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"


settings = Settings()

__all__ = ["Settings", "settings"]
