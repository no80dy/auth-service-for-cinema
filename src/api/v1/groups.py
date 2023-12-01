from uuid import UUID
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from schemas.entity import (
	GroupDetailView,
	GroupShortView,
	GroupCreate,
	GroupUpdate
)
from services.group import GroupService, get_group_service
from services.authorization import AuthorizationChecker


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
	check_authorized: AuthorizationChecker = Depends(AuthorizationChecker)
) -> GroupDetailView:
	if not await check_authorized(['create_group', ]):
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
	check_authorized: AuthorizationChecker = Depends(AuthorizationChecker)
) -> list[GroupShortView]:
	if not await check_authorized(['check_authorized', ]):
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
	check_authorized: AuthorizationChecker = Depends(AuthorizationChecker)
) -> GroupDetailView:
	if not await check_authorized(['update_group', ]):
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

	group_update_encoded = jsonable_encoder(group_update)
	# if await group_service.check_group_exists(group_update_encoded['group_name']):
	# 	raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Group with this name already exists')

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
	check_authorized: AuthorizationChecker = Depends(AuthorizationChecker)
) -> JSONResponse:
	if not await check_authorized(['delete_group', ]):
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

	group_id = await group_service.delete_group(group_id)

	if not group_id:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='group not found'
		)

	return JSONResponse(
		status_code=HTTPStatus.OK,
		content='deleted successfully'
	)
