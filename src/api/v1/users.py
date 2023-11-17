from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.entity import UserInDB, UserCreate

from db.postgres import get_session
from models.entity import User


router = APIRouter()


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
