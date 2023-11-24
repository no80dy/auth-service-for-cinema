import os
from datetime import timedelta
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
	POSTGRES_DB: str = 'users_database'
	POSTGRES_USER: str = 'postgres'
	POSTGRES_SCHEME: str = 'postgresql+asyncpg'


settings = Settings()

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Настройка конфигурации библиотеки Async FastAPI JWT Auth
class JWTSettings(BaseModel):
	authjwt_secret_key: str = 'secret'
	# Хранить и получать JWT токены из заголовков
	authjwt_token_location: set = {'headers'}
	authjwt_header_name: str = 'Authorization'
	authjwt_header_type: str = 'Bearer'
	authjwt_access_token_expires: int = timedelta(minutes=10)
	authjwt_refresh_token_expires:  int = timedelta(days=10)
	authjwt_cookie_csrf_protect: bool = False
