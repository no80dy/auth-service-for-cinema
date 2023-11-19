from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.postgres import get_session
from models.entity import Permission
from schemas.entity import PermissionInDB, PermissionName


class DatabaseSession:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def add_permission(self, data: dict) -> Permission:
		permission = Permission(**data)
		self.session.add(permission)

		await self.session.commit()
		await self.session.refresh(permission)

		return permission

	async def read_permissions(self) -> list[Permission]:
		permissions = await self.session.execute(select(Permission))
		return list(permissions.unique().scalars().all())

	async def update_permission(
		self,
		permission_id: UUID,
		data: dict
	) -> Permission | None:
		query_result = await self.session.execute(
			select(Permission)\
				.where(Permission.id == permission_id)
		)
		permission = query_result.unique().scalar()

		if not permission:
			return None

		permission.permission_name = data['permission_name']
		await self.session.commit()
		return permission

	async def delete_permission(
		self,
		permission_id: UUID
	) -> UUID | None:
		query_result = await self.session.execute(
			select(Permission)\
				.where(Permission.id == permission_id)
		)
		permission = query_result.unique().scalar()
		if not permission:
			return None
		await self.session.delete(permission)
		await self.session.commit()
		return permission.id


class PermissionService:
	def __init__(self, session: DatabaseSession):
		self.session = session

	async def add_permission(
		self,
		data: dict
	) -> PermissionInDB:
		permission = await self.session.add_permission(data)

		return PermissionInDB(
			id=permission.id,
			permission_name=permission.permission_name
		)

	async def read_permissions(self) -> list[PermissionName]:
		permissions  = await self.session.read_permissions()
		return [
			PermissionName(permission_name=permission.permission_name)
			for permission in permissions
		]

	async def update_permission(
		self,
		permission_id: UUID,
		data: dict
	) -> PermissionInDB | None:
		permission = await self.session.update_permission(permission_id, data)

		if not permission:
			return None

		return PermissionInDB(
			id=permission.id,
			permission_name=permission.permission_name
		)

	async def delete_permission(
		self,
		permission_id: UUID
	) -> UUID | None:
		deleted_id = await self.session.delete_permission(permission_id)
		return deleted_id


async def get_permission_service(
	db: AsyncSession = Depends(get_session)
) -> PermissionService:
	return PermissionService(
		DatabaseSession(db)
	)
