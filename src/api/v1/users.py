from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from schemas.entity import UserInDB, UserCreate
from services.user_services import get_user_service, UserService
from services.auth_services import AuthService, get_auth_service


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
        raise HTTPException(status_code=401, detail="Некорректное имя пользователя или пароль")

    user_email_unique = await user_service.check_unique_email(user_dto)
    if not user_email_unique:
        raise HTTPException(status_code=401, detail="Пользователь с данным email уже зарегистрирован")

    user = await user_service.create_user(user_dto)

    return user


@router.post(
    path='/login',
    response_model=UserInDB,
    status_code=HTTPStatus.OK
)
async def login(
    username: str,
    password: str,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await user_service.get_user_by_username(username)
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")
