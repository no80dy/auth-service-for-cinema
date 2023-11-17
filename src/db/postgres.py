from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from core.config import settings


Base = declarative_base()
dsn = \
	f'{settings.POSTGRES_SCHEME}://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB_NAME}'

engine = create_async_engine(dsn, echo=True, future=True)

async_session = async_sessionmaker(
	engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
	async with async_session() as session:
		yield session


async def create_database() -> None:
	async with engine.begin() as conn:
		if engine.dialect.has_schema(conn, 'users'):
			await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)
