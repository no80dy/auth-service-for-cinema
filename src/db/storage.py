from .redis import RedisStorage, INoSQLStorage

nosql_storage: RedisStorage | None = None


async def get_nosql_storage() -> RedisStorage:
    return nosql_storage


class TokenHandler:
    def __init__(self, no_sql: INoSQLStorage, expired_time: int) -> None:
        self.no_sql = no_sql
        self.expired_time = expired_time

