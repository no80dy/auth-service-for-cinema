from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.postgres import get_session
from models.entity import Permission, Group
from schemas.entity import GroupInDB, GroupRead, PermissionName


class DatabaseSession:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def delete_group(
		self,
		group_id: UUID
	) -> UUID | None:
		query_result = await self.session.execute(
			select(Group).where(Group.id == group_id)
		)
		group = query_result.scalar()

		if not group:
			return None

		await self.session.delete(group)
		await self.session.commit()

		return group.id


	async def read_groups(self) -> list[Group]:
		query_result = await self.session.execute(select(Group))
		return list(query_result.unique().scalars().all())

	async def update_group(
		self,
		group_id: UUID,
		data: dict
	) -> Group | None:
		query_result = await self.session.execute(
			select(Group).where(Group.id == group_id)
		)
		group = query_result.scalar()

		if not group:
			return None

		query_result = await self.session.execute(
			select(Permission) \
				.where(Permission.permission_name.in_(data['permissions'])
			)
		)
		permissions = list(query_result.scalars().all())

		if len(permissions) != len(data['permissions']):
			return None

		group.group_name = data['group_name']
		group.permissions = permissions
		await self.session.commit()

		return group

	async def add_group(
		self,
		data: dict
	) -> Group | None:
		query_result = await self.session.execute(
			select(Permission) \
				.where(Permission.permission_name.in_(data['permissions'])
			)
		)
		permissions = list(query_result.scalars().all())

		if len(permissions) != len(data['permissions']):
			return None

		group = Group(data['group_name'], permissions)
		self.session.add(group)

		await self.session.commit()
		await self.session.refresh(group)
		return group


class GroupService:
	def __init__(self, session: DatabaseSession):
		self.session = session

	async def create_group(
		self,
		data: dict
	) ->  GroupInDB | None:
		group = await self.session.add_group(data)

		if not group:
			return None

		return GroupInDB(
			id=group.id,
			group_name=group.group_name,
			permissions=[
				PermissionName(permission_name=permission.permission_name)
				for permission in group.permissions
			]
		)
	async def read_groups(self) -> list[GroupRead]:
		groups = await self.session.read_groups()
		return [
			GroupRead(
				group_name=group.group_name,
				permissions=[
					PermissionName(permission_name=permission.permission_name)
					for permission in group.permissions
				]
			)
			for group in groups
		]

	async def update_group(
		self,
		group_id: UUID,
		data: dict
	) -> GroupInDB | None:
		group = await self.session.update_group(group_id, data)

		if not group:
			return None

		return GroupInDB(
			id=group.id,
			group_name=group.group_name,
			permissions=[
				PermissionName(
					permission_name=permission.permission_name
				)
				for permission in group.permissions
			]
		)

	async def delete_group(
		self,
		group_id: UUID
	) -> UUID | None:
		group_id = await self.session.delete_group(group_id)

		if not group_id:
			return None

		return group_id


async def get_group_service(
	db: AsyncSession = Depends(get_session)
) -> GroupService:
	return GroupService(
		DatabaseSession(db)
	)
