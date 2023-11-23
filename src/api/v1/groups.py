from uuid import UUID
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Body
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
from services.authentication import AuthenticationService, get_authentication_service


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
	group_service: GroupService = Depends(get_group_service),
	authorize_service: AuthJWT = Depends(),
	authentication_service: AuthenticationService = Depends(get_authentication_service)
) -> GroupDetailView:
	await authorize_service.jwt_required()
	is_authorized = await authentication_service.required_permissions(
		await authorize_service.get_jwt_subject(),
		['groups.create_group']
	)

	if not is_authorized:
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

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
	response_model=list[GroupShortView],
	summary='Просмотр всех групп',
	description='Выполняет чтение всех групп',
	response_description='Имена всех групп в базе данных'
)
async def read_groups(
	group_service: GroupService = Depends(get_group_service),
	authorize_service: AuthJWT = Depends(),
	authentication_service: AuthenticationService = Depends(get_authentication_service)
) -> list[GroupShortView]:
	await authorize_service.jwt_required()
	is_authorized = await authentication_service.required_permissions(
		await authorize_service.get_jwt_subject(),
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
	group_service: GroupService = Depends(get_group_service),
	authorize_service: AuthJWT = Depends(),
	authentication_service: AuthenticationService = Depends(get_authentication_service)
) -> GroupDetailView:
	await authorize_service.jwt_required()
	is_authorized = await authentication_service.required_permissions(
		await authorize_service.get_jwt_subject(),
		['groups.update_group']
	)

	if not is_authorized:
		raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

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
	response_model=None,
	summary='Удаление группы',
	description='Выполняет удаление группы по ее идентификатору',
	response_description='Идентификатор группы'
)
async def delete_group(
	group_id: Annotated[UUID, Path(description='Идентификатор группы')],
	group_service: GroupService = Depends(get_group_service),
	authorize_service: AuthJWT = Depends(),
	authentication_service: AuthenticationService = Depends(get_authentication_service)
) -> JSONResponse:
	await authorize_service.jwt_required()
	is_authorized = await authentication_service.required_permissions(
		await authorize_service.get_jwt_subject(),
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
