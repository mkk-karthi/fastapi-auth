from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings class to load configuration from environment variables and .env file.
    """

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
    MAIL_STARTTLS: bool = True
    MAIL_FROM: str = "your_email@gmail.com"

    LOGGER_ROTATION: str = "10 MB"

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, env_file_encoding="utf-8"
    )

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"


settings = Settings()
