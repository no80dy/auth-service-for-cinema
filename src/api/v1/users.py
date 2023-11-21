import json
import datetime

from uuid import UUID
from http import HTTPStatus
from typing import Annotated
from datetime import datetime

from core.config import JWTSettings
from async_fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, Header, HTTPException

from schemas.entity import (
	UserSighIn,
	UserLoginHistoryInDb,
	UserLogoutHistoryInDb,
	RefreshToDb,
	RefreshDelDb,
	UserInDB,
	UserCreate,
	UserChangePassword,
	UserResponseUsername,
	GroupAssign
)
from services.user_services import get_user_service, UserService
from services.user import UserPermissionsService, get_user_permissions_service


router = APIRouter()


# Настройки модуля async_fastapi_jwt_auth
@AuthJWT.load_config
def get_config():
	return JWTSettings()


@router.post(
	'/{user_id}/role',
	response_model=UserInDB,
	summary='Назначение роли пользователю',
	description='Выполняет добавление новой роли для пользователя',
	response_description='Информация об обновленном пользователе'
)
async def add_role(
	user_id: UUID,
	group_assign: GroupAssign,
	user_service: UserPermissionsService = Depends(get_user_permissions_service)
):
	group_assign_encoded = jsonable_encoder(group_assign)
	user = await user_service.add_role_to_user(user_id, group_assign_encoded)
	if not user:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail='role or user not found'
		)
	return user


@router.delete(
	'/{user_id}/role',
	response_model=UserInDB,
	summary='Создание роли',
	description='Выполняет создание новой роли',
	response_description='Информация о роли, записанной в базу данных'
)
async def delete_role(
	user_id: UUID,
	group_assign: GroupAssign,
	user_service: UserPermissionsService = Depends(get_user_permissions_service)
):
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
        authorize: AuthJWT = Depends(),
) -> UserInDB | HTTPException:
	user_dto = jsonable_encoder(user_change_password)

    updated_user = await user_service.update_password(user_dto)
    if updated_user:
        # при смене пароля разлогиниваем все устройства
        await authorize.unset_jwt_cookies()
        user = await user_service.get_user_by_username(user_dto.get('username'))
        await user_service.del_all_refresh_sessions_in_db(user)

        return updated_user
    else:
        raise HTTPException(status_code=400, detail="Введены некорректные данные")


@router.post(
    path='/signin',
    response_model=UserInDB,
    status_code=HTTPStatus.OK
)
async def login(
    user_signin: UserSighIn,
    user_service: UserService = Depends(get_user_service),
    Authorize: AuthJWT = Depends(),
    user_agent: Annotated[str | None, Header()] = None,
):
	"""Вход пользователя в аккаунт."""
	if not user_agent:
		raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Вы пытаетесь зайти с неизвестного устройства')

	# проверяем валидность имени пользователя и пароля
	user = await user_service.get_user_by_username(user_signin.username)
	if not user or not user.check_password(user_signin.password):
		raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Неверное имя пользователя или пароль")

	# создаем пару access и refresh токенов
	# TODO: Записать поля с правами в тело токена?
	access_token = await Authorize.create_access_token(subject=user.username)
	refresh_token = await Authorize.create_refresh_token(subject=user.username)

	# сохраняем refresh токен и информацию об устройстве, с которого был совершен вход, в базу данных
	# TODO: проверить что не больше 5 сессий от разных устройств!

	refresh_jti = await Authorize.get_jti(refresh_token)
	session_dto = json.dumps({
		'user_id': str(user.id),
		'refresh_jti': refresh_jti,
		'user_agent': user_agent,
		'expired_at': datetime.fromtimestamp((await Authorize.get_raw_jwt(refresh_token))['exp']).isoformat(),
		'is_active': True
    })
	session = RefreshToDb.model_validate_json(session_dto)
	await user_service.put_refresh_session_in_db(session)

	# записываем историю входа в аккаунт
	history_dto = json.dumps({
		'user_id': str(user.id),
		'user_agent': user_agent,
	})
	history = UserLoginHistoryInDb.model_validate_json(history_dto)
	await user_service.put_login_history_in_db(history)

	# устанавливаем JWT куки в заголовок ответа
	await Authorize.set_access_cookies(access_token)
	await Authorize.set_refresh_cookies(refresh_token)
	return user


@router.post(
    path='/logout',
    response_model=UserInDB,
    status_code=HTTPStatus.OK
)
async def logout(
	user_service: UserService = Depends(get_user_service),
	Authorize: AuthJWT = Depends(),
	user_agent: Annotated[str | None, Header()] = None,
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

	username = await Authorize.get_jwt_subject()
	user = await user_service.get_user_by_username(username)

	# обновляем запись в таблицу истории выход из аккаунта
	history_dto = json.dumps({
		'user_id': str(user.id),
		'user_agent': user_agent,
		'logout_at': datetime.now().isoformat()
	})
	history = UserLogoutHistoryInDb.model_validate_json(history_dto)
	await user_service.put_logout_history_in_db(history)

	# удаляем сессию из таблицы refresh_sessions
	await Authorize.jwt_refresh_token_required()
	refresh_jti = (await Authorize.get_raw_jwt())['jti']
	session_dto = json.dumps({
		'user_id': str(user.id),
		'refresh_jti': refresh_jti,
		'user_agent': user_agent,
	})
	session = RefreshDelDb.model_validate_json(session_dto)
	await user_service.del_refresh_session_in_db(session)
	return user
