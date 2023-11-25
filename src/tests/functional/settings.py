from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
	REDIS_HOST: str = 'redis'
	REDIS_PORT: int = 6379

	POSTGRES_PASSWORD: str
	POSTGRES_HOST: str = 'localhost'
	POSTGRES_PORT: int = 5432
	POSTGRES_DB: str = 'users_test'
	POSTGRES_USER: str = 'postgres'
	POSTGRES_SCHEME: str = 'postgresql+asyncpg'

	SERVICE_URL: str = 'http://fastapi:8000'


test_settings = TestSettings()
