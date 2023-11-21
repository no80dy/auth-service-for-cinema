import logging
from datetime import datetime

from async_fastapi_jwt_auth import AuthJWT
from datetime import timedelta
from http import HTTPStatus
from fastapi import HTTPException

from .redis import RedisStorage, INoSQLStorage
from core.config import JWTSettings
from async_fastapi_jwt_auth import AuthJWT


nosql_storage: RedisStorage | None = None


async def get_nosql_storage() -> RedisStorage:
    return nosql_storage


class TokenHandler:
    def __init__(self, no_sql: INoSQLStorage, expired_time: int) -> None:
        self.no_sql = no_sql
        self.expired_time = expired_time

    # @AuthJWT.token_in_denylist_loader
    async def _check_if_token_in_denylist(self, decrypted_token) -> bool:
        jti = decrypted_token["jti"]
        if await self.no_sql.get(jti):
            return True
        return False

    async def check_if_token_is_valid(self, decrypted_token) -> None:
        """Метод для проверки присутствия access токена в списке невалидных токенов"""
        is_invalid_token = await self._check_if_token_in_denylist(decrypted_token)
        if is_invalid_token:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Неверное имя пользователя или пароль")

    async def put_token_in_denylist(self, decrypted_token) -> None:
        """Метод для записи access токена в список невалидных токенов"""
        jti = decrypted_token['jti']
        exp = decrypted_token['exp']
        # рассчитываем оставшееся время жизни токена (потом можно удалить, тк он просто не пройдет проверку)
        access_expires = exp - int(datetime.now().timestamp())
        await self.no_sql.set(jti, 'invalid', access_expires)
