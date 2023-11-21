from uuid import UUID
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body, Path
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from schemas.entity import (
	PermissionDetailView,
	PermissionShortView,
	PermissionCreate,
	PermissionUpdate,
)
from services.permissions import (
	PermissionService,
	get_permission_service
)

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
	permission_service: PermissionService = Depends(get_permission_service)
) -> PermissionDetailView:
	permission_create_encoded = jsonable_encoder(permission_create)
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
	permission_service: PermissionService = Depends(get_permission_service)
) -> list[PermissionShortView]:
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
	permission_service: PermissionService = Depends(get_permission_service)
) -> PermissionDetailView:
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
	response_model=None,
	summary='Удаление привелегии',
	description='Выполняет удаление конкретной привелегии',
	response_description='Идентификатор '
)
async def delete_permission(
	permission_id: Annotated[UUID, Path(description='Идентификатор привелегии')],
	permission_service: PermissionService = Depends(get_permission_service)
) -> JSONResponse:
	deleted_id = await permission_service.delete_permission(permission_id)
	if not deleted_id:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='permission not found'
		)
	return JSONResponse(
		content='deleted successfully'
	)
