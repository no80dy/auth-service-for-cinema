from .redis import RedisStorage, INoSQLStorage

nosql_storage: RedisStorage | None = None


async def get_nosql_storage() -> RedisStorage:
    return nosql_storage


class CacheUserHandler:
    def __init__(self, cache: INoSQLStorage, expired_time: int) -> None:
        self.cache = cache
        self.expired_time = expired_time

