import enum
from pathlib import Path
from tempfile import gettempdir
from typing import List, Optional

from pydantic_settings import BaseSettings
from yarl import URL
from dataclasses import dataclass

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    allowed_origin: str = "*"
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # jwt
    jwt_secret: str = "secret_key"
    jwt_algorithm: str = "HS256"

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.DEBUG
    # Variables for the database
    db_host: str = "api-db"
    db_port: int = 5432
    db_user: str = "api"
    db_pass: str = "api"
    db_base: str = "api"
    db_echo: bool = False

    # Variables for Redis
    redis_host: str = "api-redis"
    redis_port: int = 6379
    redis_user: Optional[str] = None
    redis_pass: Optional[str] = None
    redis_base: Optional[int] = None

    # Telegram bot settings
    bot_token: Optional[str] = ""
    bot_username: Optional[str] = "evildess_dev_bot"
    web_app_name: Optional[str] = "webapp"

    # channels: List = [-1002095014120, -1002074152271]

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    @property
    def redis_url(self) -> URL:
        """
        Assemble REDIS URL from settings.

        :return: redis URL.
        """
        path = ""
        if self.redis_base is not None:
            path = f"/{self.redis_base}"
        return URL.build(
            scheme="redis",
            host=self.redis_host,
            port=self.redis_port,
            user=self.redis_user,
            password=self.redis_pass,
            path=path,
        )

    class Config:
        env_file = ".env"
        env_prefix = "API_"
        env_file_encoding = "utf-8"


settings = Settings()
