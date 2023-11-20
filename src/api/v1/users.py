from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from schemas.entity import UserInDB, UserCreate, UserChangePassword, UserResponseUsername
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
        raise HTTPException(status_code=400, detail="Некорректное имя пользователя или пароль")

    user_email_unique = await user_service.check_unique_email(user_dto)
    if not user_email_unique:
        raise HTTPException(status_code=400, detail="Пользователь с данным email уже зарегистрирован")

    user = await user_service.create_user(user_dto)

    return user


@router.post(
    '/change_password/',
    response_model=UserResponseUsername,
    status_code=HTTPStatus.CREATED
)
async def change_password(
        user_change_password: UserChangePassword,
        user_service: UserService = Depends(get_user_service),
) -> UserInDB | HTTPException:
    user_dto = jsonable_encoder(user_change_password)

    updated_user = await user_service.update_password(user_dto)
    if updated_user:
        return updated_user
        # todo: добавить удаление access токена из кэша

        # todo: поменить в БД refresh токен как невалидный
    else:
        raise HTTPException(status_code=400, detail="Введены некорректные данные")
