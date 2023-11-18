from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from schemas.entity import UserInDB, UserCreate
from services.user_services import get_user_service, UserService

router = APIRouter()


@router.post(
    '/signup',
    response_model=UserInDB,
    status_code=HTTPStatus.CREATED
)
async def create_user(
        user_create: UserCreate,
        user_service: UserService = Depends(get_user_service),
) -> UserInDB | HTTPException:
    user_dto = jsonable_encoder(user_create)
    user_exist = await user_service.check_exist_user(user_dto)

    if user_exist:
        raise HTTPException(status_code=401, detail="Bad username or password")

    user = await user_service.create_user(user_dto)

    return user
