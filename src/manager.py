import asyncio

import typer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import async_session
from models.entity import User, Group, Permission



# async def create_superuser_permission_if_not_exists(session: AsyncSession) -> Permission | None:
# 	permission = (await session.execute(
# 		select(Permission).where(Permission.permission_name == '*.*')
# 	)).scalar()
# 	if not permission:
# 		new_permission = Permission('*.*')
# 		session.add(new_permission)
# 		await session.commit()
# 		await session.refresh(new_permission)
# 		return new_permission
# 	return None
#
#
# async def create_superuser_group_if_not_exists(permission: Permission, session: AsyncSession) -> Group | None:
# 	group = (await session.execute(
# 		select(Group).where(Group.group_name == 'superuser')
# 	)).scalar()
#
# 	if not group:
# 		new_group = Group('superuser', [Permission('*.*')])
# 		session.add(new_group)
# 		await session.commit()
# 		await session.refresh(new_group)
# 		return new_group
# 	return None


async def create_superuser():
	# print('Введите username:')
	# username = input()
	# print('Введите first name:')
	# first_name = input()
	# print('Введите email')
	# email = input()
	# print('Введите last name:')
	# last_name = input()
	# print('Введите password:')
	# password = input()

	async with async_session() as session:
		async with session.begin():
			# permission = await create_superuser_permission_if_not_exists(session)
			# await create_superuser_group_if_not_exists(session)

			permission = Permission('*.*')
			group = Group('superuser', [permission, ])
			user = User('superuser', 'passworderegeg', 'first_name', 'last_name', 'email')
			user.groups.append(group)
			session.add_all([permission, group, user])
		await session.commit()
		await session.refresh(user)
		print(user)
		print('User was created successfully!')


def main():
	asyncio.run(create_superuser())


if __name__ == '__main__':
	typer.run(main)
