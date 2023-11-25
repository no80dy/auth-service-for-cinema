import logging
import sys

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import (
	create_async_engine,
	AsyncSession,
	async_sessionmaker
)
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path

from .settings import test_settings
from models.entity import User, RefreshSession, UserLoginHistory


sys.path.append(str(Path(__file__).resolve().parents[3]))

from db.postgres import Base
from models.entity import Permission, Group, User, RefreshSession, UserLoginHistory


dsn = (
	f'{test_settings.POSTGRES_SCHEME}://{test_settings.POSTGRES_USER}:'
	f'{test_settings.POSTGRES_PASSWORD}@{test_settings.POSTGRES_HOST}:'
	f'{test_settings.POSTGRES_PORT}/{test_settings.POSTGRES_DB}'
)
engine = create_async_engine(dsn, echo=True, future=True)
async_session = async_sessionmaker(
	engine, class_=AsyncSession, expire_on_commit=False
)


# @pytest_asyncio.fixture(scope='session', autouse=True)
# async def init_database():
# 	async with engine.begin() as conn:
# 		await conn.run_sync(Base.metadata.drop_all)
# 		await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope='session')
async def init_session() -> AsyncSession:
	async with async_session() as session:
		yield session


@pytest_asyncio.fixture(scope='function', autouse=True)
async def clean_up_database(init_session: AsyncSession):
	for table in reversed(Base.metadata.sorted_tables):
		await init_session.execute(table.delete())
	await init_session.commit()


@pytest_asyncio.fixture(scope='function')
def create_superuser(init_session: AsyncSession):
	async def inner(username: str, password: str):
		permission = Permission('*.*')
		group = Group('superuser', [permission, ])
		user = User(username, password, username, username, username)
		user.groups.append(group)
		init_session.add_all([permission, group, user])
		await init_session.commit()
		await init_session.refresh(user)
	return inner


@pytest_asyncio.fixture(scope='function')
async def create_fake_user_in_db(init_session: AsyncSession):
	async def inner(fake_user: User) -> None:
		try:
			init_session.add(fake_user)
			await init_session.commit()
		except SQLAlchemyError as e:
			logging.error(e)
			await init_session.rollback()
	return inner


@pytest_asyncio.fixture(scope='function')
async def create_fake_session_in_db(init_session: AsyncSession):
	async def inner(fake_session: RefreshSession) -> None:
		try:
			init_session.add(fake_session)
			await init_session.commit()
			await init_session.refresh(fake_session)

		except SQLAlchemyError as e:
			logging.error(e)
			await init_session.rollback()
	return inner


@pytest_asyncio.fixture(scope='function')
async def create_fake_history_in_db(init_session: AsyncSession):
	async def inner(fake_history: UserLoginHistory) -> None:
		try:
			init_session.add(fake_history)
			await init_session.commit()
			await init_session.refresh(fake_history)

		except SQLAlchemyError as e:
			logging.error(e)
			await init_session.rollback()
	return inner
