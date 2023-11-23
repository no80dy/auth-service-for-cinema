from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.entity import User


class PermissionClaimsService:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def required_permissions(
		self,
		username: str,
		permissions: list[str]
	):
		user = (await self.session.execute(
			select(User).where(User.username == username)
		)).unique().scalar()

		permissions_in_each_group = [group.permissions for group in user.groups]
		permissions_names = []
		for permissions_group in permissions_in_each_group:
			permissions_names_group = [permission.permission_name for permission in permissions_group]
			permissions_names.extend(permissions_names_group)

		if '*.*' in permissions_names:
			return True

		for user_permission in permissions_names:
			if user_permission in permissions:
				return True
		return False


async def get_permission_claims_service(
	db: AsyncSession = Depends(get_session),
) -> PermissionClaimsService:
	return PermissionClaimsService(db)
