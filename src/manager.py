import asyncio

import typer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import async_session
from models.entity import User, Group, Permission


SUPERUSER_GROUP_NAME = 'superuser'
SUPERUSER_PERMISSION_NAME = '*.*'


async def create_superuser_group_if_not_exists(session: AsyncSession) -> None:
	group = (await session.execute(
		select(Group).where(Group.group_name == SUPERUSER_GROUP_NAME)
	)).scalar()
	if not group:
		group = Group(SUPERUSER_GROUP_NAME, [Permission('*.*')])
		session.add(group)


async def check_username_exists(username: str, session: AsyncSession):
	user = (await session.execute(
		select(User).where(User.username == username)
	)).scalars().first()

	return True if user else False


async def check_email_exists(email: str, session: AsyncSession):
	user = (await session.execute(
		select(User).where(User.username == email)
	)).scalars().first()
	return True if user else False


async def check_permission_name_exists(permission_name: str, session: AsyncSession):
	permission = (await session.execute(
		select(Permission).where(Permission.permission_name == permission_name)
	)).unique().scalars().first()
	return True if permission else False


async def check_group_name_exists(group_name: str, session: AsyncSession) -> Group:
	group = (await session.execute(
		select(Group).where(Group.group_name == group_name)
	)).unique().scalar()
	return group


async def create_superuser():
	username = input('Введите ваш логин')
	first_name = input('Введите ваше имя')
	last_name = input('Введите вашу фамилию')
	email = input('Введите ваш e-mail')
	password = input('Введите ваш пароль')

	async with async_session() as session:
		async with session.begin():
			if not await check_permission_name_exists(SUPERUSER_PERMISSION_NAME, session):
				permission = Permission(SUPERUSER_PERMISSION_NAME)
				session.add(permission)
			group = await check_group_name_exists(SUPERUSER_GROUP_NAME, session)
			if not group:
				group = Group(SUPERUSER_GROUP_NAME, [permission, ])
				session.add(group)

			if await check_username_exists(username, session):
				raise ValueError('Пользователь с таким именем уже существует')
			if await check_email_exists(email, session):
				raise ValueError('Пользователь с таким email уже существует')

			user = User(username, password, first_name, last_name, email)
			user.groups.append(group)
			session.add(user)

		await session.commit()
		await session.refresh(user)

		print('User was created successfully!')


def main():
	asyncio.run(create_superuser())


if __name__ == '__main__':
	typer.run(main)
