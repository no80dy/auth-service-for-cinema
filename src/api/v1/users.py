from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.entity import User
from schemas.entity import UserInDB, UserCreate

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

    result = await db.execute(select(User).where(User.login == user_dto.get('login')))
    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=401, detail="Bad username or password")

    user = User(**user_dto)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
