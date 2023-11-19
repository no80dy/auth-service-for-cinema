from uuid import UUID
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from schemas.entity import (
	PermissionInDB,
	PermissionCreate,
	PermissionUpdate,
	PermissionName
)
from services.permissions import (
	PermissionService,
	get_permission_service
)

router = APIRouter()


@router.post(
	'/',
	response_model=PermissionInDB,
	summary='Создание привелегии',
	description='Выполняет создание новой привелегии',
	response_description='Информация о привелегии, записанной в базу данных'
)
async def create_permission(
	permission_create: PermissionCreate,
	permission_service: PermissionService = Depends(get_permission_service)
):
	permission_create_encoded = jsonable_encoder(permission_create)
	return await permission_service.add_permission(
		permission_create_encoded
	)


@router.get(
	'/',
	response_model=list[PermissionName],
	summary='Чтение всех привелегий',
	description='Выполняет чтение всех привелегий',
	response_description='Список всех привелегий из базы данных'
)
async def read_permissions(
	permission_service: PermissionService = Depends(get_permission_service)
):
	permissions = await permission_service.read_permissions()
	return permissions


@router.put(
	'/{permission_id}',
	response_model=PermissionInDB,
	summary='Изменение привелегии',
	description='Выполняет изменение конкретной привелегии',
	response_description='Информация об измененной привелегии из базы данных'
)
async def update_permission(
	permission_id: UUID,
	permission_upate: PermissionUpdate,
	permission_service: PermissionService = Depends(get_permission_service)
) -> PermissionInDB:
	permission_update_encoded = jsonable_encoder(permission_upate)
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
	response_model=UUID,
	summary='Удаление привелегии',
	description='Выполняет удаление конкретной привелегии',
	response_description='UUID удаленной привелегии'
)
async def delete_permission(
	permission_id: UUID,
	permission_service: PermissionService = Depends(get_permission_service)
) -> UUID:
	deleted_id = await permission_service.delete_permission(permission_id)
	if not deleted_id:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='permission not found'
		)
	return deleted_id
