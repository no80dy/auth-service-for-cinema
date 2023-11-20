from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from async_fastapi_jwt_auth import AuthJWT
from core.config import JWTSettings

from schemas.entity import UserInDB, UserCreate, UserSighIn
from services.user_services import get_user_service, UserService
from services.auth_services import AuthService, get_auth_service


router = APIRouter()


# Настройки модуля async_fastapi_jwt_auth
@AuthJWT.load_config
def get_config():
    return JWTSettings()


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
    path='/signin',
    response_model=UserInDB,
    status_code=HTTPStatus.OK
)
async def login(
    user_signin: UserSighIn,
    user_service: UserService = Depends(get_user_service),
    Authorize: AuthJWT = Depends()
):
    user = await user_service.get_user_by_username(user_signin.username)
    if not user or not user.check_password(user_signin.password):
        raise HTTPException(status_code=401, detail="Bad username or password")

    # Создаем пару access и refresh токенов
    access_token = await Authorize.create_access_token(subject=user.username)
    refresh_token = await Authorize.create_refresh_token(subject=user.username)

    # Устанавливаем JWT cookies in the response
    # await Authorize.set_access_cookies(access_token)
    # await Authorize.set_refresh_cookies(refresh_token)

    return JSONResponse({'access': access_token, 'refresh': refresh_token})
