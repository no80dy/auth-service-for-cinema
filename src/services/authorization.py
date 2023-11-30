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
		permissions_names: list[str],
		endpoint_permissions: list[str]
	):
		if '*.*' in permissions_names:
			return True

		for user_permission in permissions_names:
			if user_permission in endpoint_permissions:
				return True
		return False


async def get_permission_claims_service(
	db: AsyncSession = Depends(get_session),
) -> PermissionClaimsService:
	return PermissionClaimsService(db)
