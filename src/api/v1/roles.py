from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from schemas.entity import (
	GroupInDB,
	GroupCreate,
	PermissionInDB,
	PermissionCreate,
	GroupRead,
	GroupUpdate
)
from db.postgres import get_session
from models.entity import Group, Permission

router = APIRouter()


@router.post(
	'/permissions',
	response_model=PermissionInDB,
	summary='Создание привелегии',
	description='Выполняет создание новой привелегии',
	response_description='Информация о привелегии, записанной в базу данных'
)
async def create_permission(
	permission_create: PermissionCreate,
	db: AsyncSession = Depends(get_session)
):
	permission_dto = jsonable_encoder(permission_create)
	permission = Permission(**permission_dto)
	db.add(permission)
	await db.commit()
	await db.refresh(permission)
	return permission


@router.post(
	'/roles',
	response_model=GroupInDB,
	summary='Создание роли',
	description='Выполняет создание новой роли',
	response_description='Информация о роли, записанной в базу данных'
)
async def create_role(
	group_create: GroupCreate,
	db: AsyncSession = Depends(get_session)
):
	group_dto = jsonable_encoder(group_create)
	stmt = select(Permission)\
		.where(Permission.id.in_(group_dto['permissions']))
	query_result = await db.execute(stmt)
	permissions = [
		permission[0] for permission in list(query_result.all())
	]

	group = Group(group_dto['group_name'], permissions)

	db.add(group)
	await db.commit()
	await db.refresh(group)
	return group


@router.get(
	'/roles',
	response_model=list[GroupRead],
	summary='Просмотр всех групп',
	description='Выполняет чтение всех групп',
	response_description='Имена всех групп в базе данных'
)
async def read_roles(
	db: AsyncSession = Depends(get_session)
):
	stmt = select(Group)
	groups = await db.execute(stmt)
	return [group[0] for group in groups.all()]


@router.put(
	'/roles/{group_id}',
	response_model=GroupInDB,
	summary='Обновление данных о жанре',
	description='Выполняет обновление данных о жанре',
	response_description='Обновленные данные группы из базы данных'
)
async def update_role(
	group_id: UUID,
	group_update: GroupUpdate,
	db: AsyncSession = Depends(get_session)
):
	group_update_encoded = jsonable_encoder(group_update)
	group = await db.get(Group, group_id)
	stmt = select(Permission)\
		.where(Permission.id.in_(group_update_encoded['permissions']))
	query_result = await db.execute(stmt)
	permissions = [
		permission[0] for permission in list(query_result.all())
	]

	group.group_name = group_update_encoded['group_name']
	group.permissions = permissions
	await db.commit()
	return group


@router.delete(
	'/roles/{group_id}',
	response_model=dict,
	summary='Изменение',
	description='Выполняет чтение всех групп',
	response_description='Имена всех групп в базе данных'
)
async def delete_role(
	group_id: UUID,
	db: AsyncSession = Depends(get_session)
):
	group = await db.get(Group, group_id)
	await db.delete(group)
	await db.commit()
	return {
		"body": "group deleted successfully"
	}
