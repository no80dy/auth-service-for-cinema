from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.postgres import get_session
from models.entity import Permission
from schemas.entity import PermissionDetailView, PermissionShortView


class DatabaseSession:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def get_permission_by_name(self, permission_name: str):
		permission = (await self.session.execute(
			select(Permission).where(
				Permission.permission_name == permission_name
			)
		)).unique().scalars().all()
		return permission

	async def add_permission(self, data: dict) -> Permission:
		permission = Permission(**data)
		self.session.add(permission)

		await self.session.commit()
		await self.session.refresh(permission)

		return permission

	async def read_permissions(self) -> list[Permission]:
		permissions = await self.session.execute(select(Permission))
		return list(permissions.unique().scalars().all())

	async def get_permission_name_duplicates(
		self,
		permission_id: UUID,
		permission_name: str
	) -> list[Permission]:
		permission_duplicates = (await self.session.execute(
			select(Permission).where(
				and_(
					Permission.id != permission_id,
					Permission.permission_name == permission_name
				)
			)
		)).scalars().all()

		return list(permission_duplicates)

	async def update_permission(
		self,
		permission_id: UUID,
		data: dict
	) -> Permission | None:
		query_result = await self.session.execute(
			select(Permission).where(Permission.id == permission_id)
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
			select(Permission).where(Permission.id == permission_id)
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

	async def check_permission_exists(self, permission_name: str) -> bool:
		permission = await self.session.get_permission_by_name(permission_name)
		return bool(permission)

	async def add_permission(
		self,
		data: dict
	) -> PermissionDetailView:
		permission = await self.session.add_permission(data)

		return PermissionDetailView(
			id=permission.id,
			permission_name=permission.permission_name
		)

	async def read_permissions(self) -> list[PermissionShortView]:
		permissions = await self.session.read_permissions()
		return [
			PermissionShortView(permission_name=permission.permission_name)
			for permission in permissions
		]

	async def check_permission_name_duplicates(
		self,
		permission_id: UUID,
		permission_name: str
	) -> bool:
		return bool(await self.session.get_permission_name_duplicates(permission_id, permission_name))

	async def update_permission(
		self,
		permission_id: UUID,
		data: dict
	) -> PermissionDetailView | None:
		permission = await self.session.update_permission(permission_id, data)

		if not permission:
			return None

		return PermissionDetailView(
			id=permission.id,
			permission_name=permission.permission_name
		)

	async def delete_permission(
		self,
		permission_id: UUID
	) -> UUID | None:
		return await self.session.delete_permission(permission_id)


async def get_permission_service(
	db: AsyncSession = Depends(get_session)
) -> PermissionService:
	return PermissionService(
		DatabaseSession(db)
	)
