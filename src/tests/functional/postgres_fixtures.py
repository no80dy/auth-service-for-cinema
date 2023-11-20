import sys
import pytest_asyncio

from sqlalchemy.ext.asyncio import (
	create_async_engine,
	AsyncSession,
	async_sessionmaker
)
from pathlib import Path

from .settings import test_settings

sys.path.append(str(Path(__file__).resolve().parents[3]))

from db.postgres import Base


dsn = (
	f'{test_settings.POSTGRES_SCHEME}://{test_settings.POSTGRES_USER}:'
	f'{test_settings.POSTGRES_PASSWORD}@{test_settings.POSTGRES_HOST}:'
	f'{test_settings.POSTGRES_PORT}/{test_settings.POSTGRES_DB_NAME}'
)
engine = create_async_engine(dsn, echo=True, future=True)
async_session = async_sessionmaker(
	engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope='function', autouse=True)
async def init_database():
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)
		await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope='session')
async def init_session() -> AsyncSession:
	async with async_session() as session:
		yield session
