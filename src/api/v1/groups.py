from uuid import UUID
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from async_fastapi_jwt_auth import AuthJWT

from schemas.entity import (
	GroupDetailView,
	GroupShortView,
	GroupCreate,
	GroupUpdate
)
from services.group import GroupService, get_group_service
from services.authorization import PermissionClaimsService, get_permission_claims_service


security = HTTPBearer()
router = APIRouter()


@router.post(
	'/',
	response_model=GroupDetailView,
	summary='Создание группы',
	description='Выполняет создание новой роли',
	response_description='Информация о роли, записанной в базу данных'
)
async def create_group(
	group_create: Annotated[GroupCreate, Body(description='Шаблон для создания группы')],
	group_service: Annotated[GroupService, Depends(get_group_service)],
	permission_claims_service: Annotated[PermissionClaimsService, Depends(get_permission_claims_service)],
	authorize: Annotated[AuthJWT, Depends()],
	access_token: Annotated[str, Depends(security)]
) -> GroupDetailView:
	await authorize.jwt_required(token=access_token)
	is_authorized = await permission_claims_service.required_permissions(
		await authorize.get_jwt_subject(),
		['groups.create_group']
	)

	if not is_authorized:
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

	group_create_encoded = jsonable_encoder(group_create)
	if await group_service.check_group_exists(group_create_encoded['group_name']):
		raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Group with this name already exists')

	group = await group_service.create_group(group_create_encoded)
	if not group:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='permissions not found'
		)
	return group


@router.get(
	'/',
	response_model=list[GroupShortView],
	summary='Просмотр всех групп',
	description='Выполняет чтение всех групп',
	response_description='Имена всех групп в базе данных'
)
async def read_groups(
	group_service: Annotated[GroupService, Depends(get_group_service)],
	permission_claims_service: Annotated[PermissionClaimsService, Depends(get_permission_claims_service)],
	authorize: Annotated[AuthJWT, Depends()],
	access_token: Annotated[str, Depends(security)]
) -> list[GroupShortView]:
	await authorize.jwt_required(token=access_token)
	is_authorized = await permission_claims_service.required_permissions(
		await authorize.get_jwt_subject(),
		['groups.read_groups']
	)

	if not is_authorized:
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

	return await group_service.read_groups()


@router.put(
	'/{group_id}',
	response_model=GroupDetailView,
	summary='Обновление данных о жанре',
	description='Выполняет обновление данных о жанре',
	response_description='Обновленные данные группы из базы данных'
)
async def update_group(
	group_id: Annotated[UUID, Path(description='Идентификатор группы')],
	group_update: Annotated[GroupUpdate, Body(description='Шаблон для изменения группы')],
	group_service: Annotated[GroupService, Depends(get_group_service)],
	authorize: Annotated[AuthJWT, Depends()],
	permission_claims_service: Annotated[PermissionClaimsService, Depends(get_permission_claims_service)],
	access_token: Annotated[str, Depends(security)]
) -> GroupDetailView:
	await authorize.jwt_required(token=access_token)
	is_authorized = await permission_claims_service.required_permissions(
		await authorize.get_jwt_subject(),
		['groups.update_group']
	)

	if not is_authorized:
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

	group_update_encoded = jsonable_encoder(group_update)
	if await group_service.check_group_exists(group_update_encoded['group_name']):
		raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Group with this name already exists')

	group = await group_service.update_group(group_id, group_update_encoded)
	if not group:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='group or permission not found'
		)
	return group

@router.delete(
	'/{group_id}',
	response_model=None,
	summary='Удаление группы',
	description='Выполняет удаление группы по ее идентификатору',
	response_description='Идентификатор группы'
)
async def delete_group(
	group_id: Annotated[UUID, Path(description='Идентификатор группы')],
	group_service: Annotated[GroupService, Depends(get_group_service)],
	authorize: Annotated[AuthJWT, Depends()],
	permission_claims_service: Annotated[PermissionClaimsService, Depends(get_permission_claims_service)],
	access_token: Annotated[str, Depends(security)]
) -> JSONResponse:
	await authorize.jwt_required(token=access_token)
	is_authorized = await permission_claims_service.required_permissions(
		await authorize.get_jwt_subject(),
		['groups.delete_group']
	)

	if not is_authorized:
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

	group_id = await group_service.delete_group(group_id)

	if not group_id:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='group not found'
		)

	return JSONResponse(
		content='deleted successfully'
	)
