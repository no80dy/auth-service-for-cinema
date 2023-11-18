from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.postgres import get_session
from models.entity import Permission
from schemas.entity import PermissionInDB

class PermissionService:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def add_permission_in_database(
		self,
		data: dict
	) -> PermissionInDB:
		permission = Permission(**data)
		self.session.add(permission)

		await self.session.commit()
		await self.session.refresh(permission)

		return PermissionInDB(
			id=permission.id,
			permission_name=permission.permission_name
		)


async def get_permission_service(
	db: AsyncSession = Depends(get_session)
) -> PermissionService:
	return PermissionService(db)
