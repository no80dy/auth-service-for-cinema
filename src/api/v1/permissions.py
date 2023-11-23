from uuid import UUID
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body, Path
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from async_fastapi_jwt_auth import AuthJWT

from schemas.entity import (
	PermissionDetailView,
	PermissionShortView,
	PermissionCreate,
	PermissionUpdate,
)
from services.permissions import (
	PermissionService,
	get_permission_service,
)
from services.authentication import (
	AuthenticationService,
	get_authentication_service
)


security = HTTPBearer()
router = APIRouter()


@router.post(
	'/',
	response_model=PermissionDetailView,
	summary='Создание привелегии',
	description='Выполняет создание новой привелегии',
	response_description='Полная информация о привелегии'
)
async def create_permission(
	permission_create: Annotated[PermissionCreate, Body(description='Шаблон для создания привелегии')],
	permission_service: PermissionService = Depends(get_permission_service),
	authorize_service: AuthJWT = Depends(),
	authentication_service: AuthenticationService = Depends(get_authentication_service),
	authorization: str = Depends(security)
) -> PermissionDetailView:

	await authorize_service.jwt_required()
	is_authorized = await authentication_service.required_permissions(
		await authorize_service.get_jwt_subject(),
		['permissions.create_permission']
	)

	if not is_authorized:
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

	permission_create_encoded = jsonable_encoder(permission_create)
	if await permission_service.check_permission_exists(permission_create_encoded['permission_name']):
		raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Permission with this name already exists')

	return await permission_service.add_permission(
		permission_create_encoded
	)


@router.get(
	'/',
	response_model=list[PermissionShortView],
	summary='Чтение всех привелегий',
	description='Выполняет чтение всех привелегий',
	response_description='Список привелегий с краткой информацией'
)
async def read_permissions(
	permission_service: PermissionService = Depends(get_permission_service),
	authorize_service: AuthJWT = Depends(),
	authentication_service: AuthenticationService = Depends(get_authentication_service),
	authorization: str = Depends(security)
) -> list[PermissionShortView]:
	await authorize_service.jwt_required()
	is_authorized = await authentication_service.required_permissions(
		await authorize_service.get_jwt_subject(),
		['permissions.read_permissions']
	)

	if not is_authorized:
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

	permissions = await permission_service.read_permissions()
	return permissions


@router.put(
	'/{permission_id}',
	response_model=PermissionDetailView,
	summary='Изменение привелегии',
	description='Выполняет изменение конкретной привелегии',
	response_description='Информация об измененной привелегии из базы данных'
)
async def update_permission(
	permission_id: Annotated[UUID, Path(description='Идентификатор привелегии')],
	permission_upate: Annotated[PermissionUpdate, Body(description='Шаблон для обновления привелегии')],
	permission_service: PermissionService = Depends(get_permission_service),
	authorize_service: AuthJWT = Depends(),
	authentication_service: AuthenticationService = Depends(get_authentication_service),
	authorization: str = Depends(security)
) -> PermissionDetailView:
	await authorize_service.jwt_required()
	is_authorized = await authentication_service.required_permissions(
		await authorize_service.get_jwt_subject(),
		['permissions.update_permission']
	)

	if not is_authorized:
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

	permission_update_encoded = jsonable_encoder(permission_upate)
	if await permission_service.check_permission_exists(permission_update_encoded['permission_name']):
		raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Permission with this name already exists')

	permission = await permission_service.update_permission(
		permission_id, permission_update_encoded
	)
	if not permission:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='Permisson not found'
		)

	return permission


@router.delete(
	'/{permission_id}',
	response_model=None,
	summary='Удаление привелегии',
	description='Выполняет удаление конкретной привелегии',
	response_description='Идентификатор '
)
async def delete_permission(
	permission_id: Annotated[UUID, Path(description='Идентификатор привелегии')],
	permission_service: PermissionService = Depends(get_permission_service),
	authorize_service: AuthJWT = Depends(),
	authentication_service: AuthenticationService = Depends(get_authentication_service),
	authorization: str = Depends(security)
) -> JSONResponse:
	await authorize_service.jwt_required()
	is_authorized = await authentication_service.required_permissions(
		await authorize_service.get_jwt_subject(),
		['permissions.delete_permission']
	)

	if not is_authorized:
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

	deleted_id = await permission_service.delete_permission(permission_id)
	if not deleted_id:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='permission not found'
		)
	return JSONResponse(
		content='deleted successfully'
	)
