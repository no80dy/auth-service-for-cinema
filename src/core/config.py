import os

from typing import Any
from logging import config as logging_config

from pydantic import PostgresDsn, field_validator, ValidationInfo
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from core.logger import LOGGING


class Settings(BaseSettings):
	PROJECT_NAME: str = 'auth'
	REDIS_HOST: str = 'redis'
	REDIS_PORT: int = 6379

	POSTGRES_PASSWORD: str
	POSTGRES_HOST: str = 'localhost'
	POSTGRES_PORT: int = 5432
	POSTGRES_DB_NAME: str = 'users_database'
	POSTGRES_USER: str = 'postgres'
	POSTGRES_SCHEME: str = 'postgresql+asyncpg'


settings = Settings()

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Async FastAPI JWT Auth module settings
class JWTSettings(BaseModel):
	authjwt_secret_key: str = "secret"

