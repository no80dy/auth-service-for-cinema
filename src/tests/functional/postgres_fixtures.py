import sys

import pytest
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
from models.entity import Permission, Group, User, RefreshSession, UserLoginHistory


dsn = (
	f'{test_settings.POSTGRES_SCHEME}://{test_settings.POSTGRES_USER}:'
	f'{test_settings.POSTGRES_PASSWORD}@{test_settings.POSTGRES_HOST}:'
	f'{test_settings.POSTGRES_PORT}/{test_settings.POSTGRES_DB_NAME}'
)
engine = create_async_engine(dsn, echo=True, future=True)
async_session = async_sessionmaker(
	engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def init_database():
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)
		await conn.run_sync(Base.metadata.create_all)


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
def write_groups_without_permissions_in_database(init_session: AsyncSession):
	async def inner(groups_names: list[str]):
		for group_name in groups_names:
			init_session.add(Group(group_name, []))
		await init_session.commit()
	return inner


@pytest_asyncio.fixture(scope='function')
def write_groups_with_permissions_in_database(init_session: AsyncSession):
	async def inner(groups_names: list[str], permissions_names: list[str]):
		permissions = [
			Permission(permission_name) for permission_name in permissions_names
		]
		groups = [
			Group(group_name, permissions) for group_name in groups_names
		]
		init_session.add_all(permissions)
		init_session.add_all(groups)
		await init_session.commit()
	return inner


@pytest_asyncio.fixture(scope='function')
def fill_database(init_session: AsyncSession):
	async def inner(permissions_names: list[str], groups_names: list[str], users_fillers: list[str]):
		permissions = [Permission(permission_name) for permission_name in permissions_names]
		groups = [Group(group_name, permissions) for group_name in groups_names]
		users = [
			User(user_filler, user_filler, user_filler, user_filler, user_filler)
			for user_filler in users_fillers
		]
		init_session.add_all([permissions, groups, users])
		await init_session.commit()
		await init_session.refresh(permissions)
		await init_session.refresh(groups)
		await init_session.refresh(users)
		return permissions, groups, users
	return inner

@pytest_asyncio.fixture(scope='function')
def create_groups(init_session: AsyncSession):
	async def inner(permissions_names: list[str]) -> list[Permission]:
		permissions = [Permission(permission_name) for permission_name in permissions_names]
		init_session.add_all(permissions)
		await init_session.commit()
		await init_session.refresh(permissions)
		return permissions
	return inner


@pytest_asyncio.fixture(scope='function')
def create_group_with_permissions(init_session: AsyncSession):
	async def inner(group_name: str, permissions_names: list[str]):
		permissions = [
			Permission(permission_name) for permission_name in permissions_names
		]
		group = Group(group_name, permissions)
		init_session.add_all(permissions)
		init_session.add(group)
		await init_session.commit()
		await init_session.refresh(group)
		return group
	return inner


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
