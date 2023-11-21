from async_fastapi_jwt_auth import AuthJWT

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

    @AuthJWT.token_in_denylist_loader
    async def check_if_token_in_denylist(self, decrypted_token):
        jti = decrypted_token["jti"]
        entry = self.no_sql.get(jti)
        return entry and entry == "true"

    async def put_access_token_in_denylist(self, Authorize: AuthJWT) -> None:
        jti = (await Authorize.get_raw_jwt())["jti"]
        self.no_sql.set(jti, 'invalid', JWTSettings.access_expires)
