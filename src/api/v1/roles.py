from uuid import UUID
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
# TODO: For delete endpoint
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from schemas.entity import (
	GroupInDB,
	GroupCreate,
	GroupRead,
	GroupUpdate
)
from services.group import GroupService, get_group_service

router = APIRouter()


@router.post(
	'/',
	response_model=GroupInDB,
	summary='Создание роли',
	description='Выполняет создание новой роли',
	response_description='Информация о роли, записанной в базу данных'
)
async def create_role(
	group_create: GroupCreate,
	group_service: GroupService = Depends(get_group_service)
) -> GroupInDB:
	group_create_encoded = jsonable_encoder(group_create)
	group = await group_service.create_group(group_create_encoded)
	if not group:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='permissions not found'
		)
	return group


@router.get(
	'/',
	response_model=list[GroupRead],
	summary='Просмотр всех групп',
	description='Выполняет чтение всех групп',
	response_description='Имена всех групп в базе данных'
)
async def read_roles(
	group_service: GroupService = Depends(get_group_service)
) -> list[GroupRead]:
	return await group_service.read_groups()


@router.put(
	'/{group_id}',
	response_model=GroupInDB,
	summary='Обновление данных о жанре',
	description='Выполняет обновление данных о жанре',
	response_description='Обновленные данные группы из базы данных'
)
async def update_role(
	group_id: UUID,
	group_update: GroupUpdate,
	group_service: GroupService = Depends(get_group_service)
) -> GroupInDB:
	group_update_encoded = jsonable_encoder(group_update)
	group = await group_service.update_group(group_id, group_update_encoded)
	if not group:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='group or permission not found'
		)
	return group

@router.delete(
	'/{group_id}',
	response_model=dict,
	summary='Изменение',
	description='Выполняет чтение всех групп',
	response_description='Имена всех групп в базе данных'
)
async def delete_role(
	group_id: UUID,
	group_service: GroupService = Depends(get_group_service)
) -> dict:
	group_id = await group_service.delete_group(group_id)

	if not group_id:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='group not found'
		)

	return {
		'body': f'deleted {group_id}'
	}
