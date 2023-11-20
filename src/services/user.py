from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.postgres import get_session
from models.entity import User, Group
from schemas.entity import UserInDB


class DatabaseSession:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def add_role_to_user(
		self,
		user_id: UUID,
		data: dict
	) -> User | None:
		user = (
			await self.session.execute(
				select(User).where(User.id == user_id)
			)
		).scalar()

		if not user:
			return None

		group = (
			await self.session.execute(
				select(Group).where(Group.id == UUID(data['group_id']))
			)
		).scalar()

		if not group:
			return None

		user.groups.append(group)
		await self.session.commit()

		return user

	async def delete_role_from_user(
		self,
		user_id: UUID,
		data: dict
	) -> User | None:
		user = (
			await self.session.execute(
				select(User).where(User.id == user_id)
			)
		).scalar()

		if not user:
			return None

		group = (
			await self.session.execute(
				select(Group).where(Group.id == UUID(data['group_id']))
			)
		).scalar()

		if not group:
			return None

		user.groups.remove(group)
		await self.session.commit()

		return user


class UserPermissionsService:
	def __init__(self, session: DatabaseSession):
		self.session = session

	async def add_role_to_user(
		self,
		user_id: UUID,
		data: dict
	) -> UserInDB | None:
		user = await self.session.add_role_to_user(user_id, data)

		if not user:
			return None

		return UserInDB(
			id=user.id,
			first_name=user.first_name,
			last_name=user.last_name,
			groups=[group.id for group in user.groups]
		)

	async def delete_role_from_user(
		self,
		user_id: UUID,
		data: dict
	) -> UserInDB | None:
		user = await self.session.delete_role_from_user(user_id, data)

		if not user:
			return None

		return UserInDB(
			id=user.id,
			first_name=user.first_name,
			last_name=user.last_name,
			groups=[group.id for group in user.groups]
		)


async def get_user_permissions_service(
	db: AsyncSession = Depends(get_session)
) -> UserPermissionsService:
	return UserPermissionsService(
		DatabaseSession(db)
	)
