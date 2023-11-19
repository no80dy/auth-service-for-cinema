from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.entity import UserInDB, UserCreate, GroupAssign

from db.postgres import get_session
from models.entity import User
from services.user import UserService, get_user_service


router = APIRouter()


@router.post(
	'/{user_id}/role',
	response_model=UserInDB,
	summary='Создание роли',
	description='Выполняет создание новой роли',
	response_description='Информация о роли, записанной в базу данных'
)
async def add_role(
	user_id: UUID,
	group_assign: GroupAssign,
	user_service: UserService = Depends(get_user_service)
):
	group_assign_encoded = jsonable_encoder(group_assign)
	user = await user_service.add_role_to_user(user_id, group_assign_encoded)
	if not user:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='role or user not found'
		)
	return user


@router.post(
	'/signup',
	response_model=UserInDB,
	status_code=HTTPStatus.CREATED
)
async def create_user(
	user_create: UserCreate,
	db: AsyncSession = Depends(get_session)
) -> UserInDB:
	user_dto = jsonable_encoder(user_create)
	user = User(**user_dto)
	db.add(user)
	await db.commit()
	await db.refresh(user)
	return user
