import json
import datetime

from uuid import UUID
from http import HTTPStatus
from typing import Annotated
from datetime import datetime

from async_fastapi_jwt_auth import AuthJWT
from fastapi.security import HTTPBearer
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi import APIRouter, Depends, Header, HTTPException, Path, Body, Query

from core.config import JWTSettings
from schemas.entity import (
    UserSighIn,
    UserInDB,
    UserCreate,
    UserChangePassword,
    UserResponseUsername,
    GroupAssign,
    UserPaginatedHistoryInDb,
)
from services.user_services import get_user_service, UserService
from services.user import UserPermissionsService, get_user_permissions_service
from services.authorization import PermissionClaimsService, get_permission_claims_service

MAX_SESSION_NUMBER = 5

security = HTTPBearer()
router = APIRouter()


# Настройки модуля async_fastapi_jwt_auth
@AuthJWT.load_config
def get_config():
    return JWTSettings()


@router.post(
    '/{user_id}/group',
    response_model=UserInDB,
    summary='Назначение роли пользователю',
    description='Выполняет добавление новой роли для пользователя',
    response_description='Информация об обновленном пользователе'
)
async def add_group(
        user_id: Annotated[UUID, Path(description='Идентификатор пользователя')],
        group_assign: Annotated[GroupAssign, Body(description='Шаблон создания роли для пользователя')],
        user_service: Annotated[UserPermissionsService, Depends(get_user_permissions_service)],
        permission_claims_service: Annotated[PermissionClaimsService, Depends(get_permission_claims_service)],
        authorize: Annotated[AuthJWT, Depends()],
        access_token: Annotated[str, Depends(security)]
):
    await authorize.jwt_required(token=access_token)
    is_authorized = await permission_claims_service.required_permissions(
        await authorize.get_jwt_subject(), ['add_group', ]
    )

    if not is_authorized:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

    group_assign_encoded = jsonable_encoder(group_assign)
    user = await user_service.add_role_to_user(user_id, group_assign_encoded)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='role or user not found'
        )
    return user


@router.delete(
    '/{user_id}/group',
    response_model=UserInDB,
    summary='Создание роли',
    description='Выполняет создание новой роли',
    response_description='Информация о роли, записанной в базу данных'
)
async def delete_group(
        user_id: Annotated[UUID, Path(description='Идентификатор пользователя')],
        group_assign: Annotated[GroupAssign, Body(description='Шаблон удаления роли для пользователя')],
        user_service: Annotated[UserPermissionsService, Depends(get_user_permissions_service)],
        authorize: Annotated[AuthJWT, Depends()],
        permission_claims_service: Annotated[PermissionClaimsService, Depends(get_permission_claims_service)],
        access_token: Annotated[str, Depends(security)]
):
    await authorize.jwt_required(token=access_token)
    is_authorized = await permission_claims_service.required_permissions(
        await authorize.get_jwt_subject(), ['delete_group', ]
    )

    if not is_authorized:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough rights')

    group_assign_encoded = jsonable_encoder(group_assign)
    user = await user_service.delete_role_from_user(user_id, group_assign_encoded)
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
        user_service: UserService = Depends(get_user_service),
) -> UserInDB | HTTPException:
    user_dto = jsonable_encoder(user_create)

    repeated_pass_true = await user_service.check_repeated_password(user_dto.get('password'), user_dto.get('password'))

    user_exist = await user_service.check_exist_user(user_dto)
    if not repeated_pass_true or user_exist:
        raise HTTPException(status_code=400, detail="Некорректное имя пользователя или пароль")

    user_email_unique = await user_service.check_unique_email(user_dto)
    if not user_email_unique:
        raise HTTPException(status_code=400, detail="Пользователь с данным email уже зарегистрирован")

    user = await user_service.create_user(user_dto)
    return user


@router.post(
    '/change_password/',
    response_model=UserResponseUsername,
    status_code=HTTPStatus.OK
)
async def change_password(
        user_change_password: UserChangePassword,
        user_service: UserService = Depends(get_user_service),
) -> UserInDB | HTTPException:
    user_dto = jsonable_encoder(user_change_password)

    updated_user = await user_service.update_password(user_dto)
    if updated_user:
        # при смене пароля разлогиниваем все устройства
        user = await user_service.get_user_by_username(user_dto.get('username'))
        await user_service.del_all_refresh_sessions_in_db(user)

        return updated_user
    else:
        raise HTTPException(status_code=400, detail="Введены некорректные данные")


@router.post(
    path='/signin',
    response_model=UserInDB,
    status_code=HTTPStatus.OK,
    summary='Вход пользователя в аккаунт',
    description='На основании логина и пароля формирует пару access и refresh токенов',
    response_description='Аутентификация пользователя по логину и паролю'
)
async def login(
        user_signin: UserSighIn,
        user_service: UserService = Depends(get_user_service),
        Authorize: AuthJWT = Depends(),
        user_agent: Annotated[str | None, Header()] = None,
):
    """Вход пользователя в аккаунт."""
    if not user_agent:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Вы пытаетесь зайти с неизвестного устройства'
        )

    # проверяем валидность имени пользователя и пароля
    user = await user_service.get_user_by_username(user_signin.username)
    if not user or not user.check_password(user_signin.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    # проверяем, что пользователь уже не вошел с данного устройства
    active_user_login = await user_service.check_if_user_login(str(user.id), user_agent)
    if active_user_login:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={'detail': 'Данный пользователь уже совершил вход с данного устройства'})

    user_claims = {
        'user_id': str(user.id),
        'permissions': await user_service.get_user_permissions(user.id)
    }

    # создаем пару access и refresh токенов
    access_token = await Authorize.create_access_token(
        subject=user.username,
        user_claims=user_claims
    )
    refresh_token = await Authorize.create_refresh_token(
        subject=user.username,
        user_claims=user_claims
    )

    # защита от превышения максимально возможного количества сессий
    session_number = await user_service.count_refresh_sessions(str(user.id))
    if session_number > MAX_SESSION_NUMBER:
        await user_service.del_all_refresh_sessions_in_db(user)

    decrypted_token = await Authorize.get_raw_jwt(refresh_token)
    await user_service.put_refresh_session_in_db(str(user.id), user_agent, decrypted_token)

    # записываем историю входа в аккаунт
    await user_service.put_login_history_in_db(str(user.id), user_agent)

    return JSONResponse(content={
        'access_token': access_token,
        'refresh_token': refresh_token
    })


@router.post(
    path='/logout',
    status_code=HTTPStatus.OK,
    summary='Выход пользователя из аккаунта',
    description='Делает невалидными текущие access и refresh токены',
)
async def logout(
        user_service: UserService = Depends(get_user_service),
        Authorize: AuthJWT = Depends(),
        user_agent: Annotated[str | None, Header()] = None,
        authorization: str = Depends(security)
):
    """Выход пользователя из аккаунта."""
    if not user_agent:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Вы пытаетесь зайти с неизвестного устройства')

    # проверяем наличие и валидность access токена
    await Authorize.jwt_required()

    # проверяем, что access токен не в списке невалидных токенов
    decrypted_token = await Authorize.get_raw_jwt()
    await user_service.token_handler.check_if_token_is_valid(decrypted_token)

    # записываем текущий access токен в список невалидных токенов
    await user_service.token_handler.put_token_in_denylist(decrypted_token)

    user_id = decrypted_token['user_id']

    # обновляем запись в таблицу истории выход из аккаунта
    await user_service.put_logout_history_in_db(user_id, user_agent)

    # удаляем сессию из таблицы refresh_sessions
    await user_service.del_refresh_session_in_db(user_id, user_agent)

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={'detail': 'Выход осуществлен успешно'})


@router.post(
    path='/refresh-tokens',
    status_code=HTTPStatus.OK,
    summary='Обновление пары access и refresh токенов',
    description='Получить новый access токен на основании валидного refresh токена',
)
async def refresh(
        user_service: UserService = Depends(get_user_service),
        Authorize: AuthJWT = Depends(),
        user_agent: Annotated[str | None, Header()] = None,
        authorization: str = Depends(security),
):
    """Обновление пары access и refresh токенов."""
    if not user_agent:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Вы пытаетесь зайти с неизвестного устройства',
        )

    # проверяем наличие и валидность refresh токена
    await Authorize.jwt_refresh_token_required()

    decrypted_token = await Authorize.get_raw_jwt()
    user_id = decrypted_token['user_id']

    # удаляем сессию из таблицы refresh_sessions
    session_exist = await user_service.check_if_session_exist(user_id, user_agent)
    if session_exist:
        await user_service.del_refresh_session_in_db(user_id, user_agent)
    else:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Невалидный токен для данного устройства',
        )

    # создаем пару access и refresh токенов
    username = await Authorize.get_jwt_subject()
    user_claims = {
        'user_id': user_id,
        'permissions': await user_service.get_user_permissions(user_id)
    }

    access_token = await Authorize.create_access_token(
        subject=username,
        user_claims=user_claims
    )
    refresh_token = await Authorize.create_refresh_token(
        subject=username,
        user_claims=user_claims
    )

    # сохраняем refresh токен и информацию об устройстве, с которого был совершен вход, в базу данных
    new_decrypted_token = await Authorize.get_raw_jwt(refresh_token)
    await user_service.put_refresh_session_in_db(user_id, user_agent, new_decrypted_token)

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={
            'access_token': access_token,
            'refresh_token': refresh_token,
        })


@router.get(
    '/{user_id}/get_history',
    response_model=UserPaginatedHistoryInDb,
    status_code=HTTPStatus.OK,
)
async def get_history(
        user_id: UUID,
        page_size: int = Query(ge=1, default=2),
        page_number: int = Query(ge=1, default=1),
        user_service: UserService = Depends(get_user_service),
):
    history = await user_service.get_login_history(user_id, page_size, page_number)
    count = await user_service.get_login_history_count(user_id)
    previous, next_page = await user_service.calc_previous_and_next_pages(page_number, page_size, count)

    result = {
        'previous': previous,
        'next': next_page,
        'items': history
    }

    return result
