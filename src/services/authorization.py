from fastapi import Depends
from fastapi.security import HTTPBearer
from async_fastapi_jwt_auth import AuthJWT


security = HTTPBearer()


class AuthorizationChecker:
	def __init__(
		self,
		access_token: str = Depends(security),
		authorize_service: AuthJWT = Depends(),
	):
		self.access_token = access_token
		self.authorize_service = authorize_service

	async def __call__(
		self,
		required_permissons: list[str]
	):
		await self.authorize_service.jwt_required(token=self.access_token)
		user_permissions = (await self.authorize_service.get_raw_jwt())['permissions']

		if '*.*' in user_permissions:
			return True

		for user_permission in user_permissions:
			if user_permission in required_permissons:
				return True

		return False


# async def required_authorization(
# 	required_permissons: list[str],
# 	access_token: str = Depends(security),
# 	authorize_service: AuthJWT = Depends(),
# ):
# 	await authorize_service.jwt_required(token=access_token)
# 	user_permissions = (await authorize_service.get_raw_jwt())['permissions']
#
# 	if '*.*' in user_permissions:
# 		return True
#
# 	for user_permission in user_permissions:
# 		if user_permission in required_permissons:
# 			return True
#
# 	return False


class PermissionClaimsService:

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


async def get_permission_claims_service() -> PermissionClaimsService:
	return PermissionClaimsService()
