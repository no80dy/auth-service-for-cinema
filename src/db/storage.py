from .redis import RedisStorage, INoSQLStorage

nosql_storage: RedisStorage | None = None


async def get_nosql_storage() -> RedisStorage:
    return nosql_storage


class CacheUserHandler:
    def __init__(self, cache: INoSQLStorage, expired_time: int) -> None:
        self.cache = cache
        self.expired_time = expired_time

    # async def get_film(self, key: str) -> None | Film | list[Film] | Any:
    #     data = await self.cache.get(key)
    #     if not data:
    #         return None
    #
    #     if '/' not in key:
    #         return Film.model_validate_json(data)
    #     return [Film.model_validate_json(obj) for obj in json.loads(data)]
    #
    # async def put_film(self, key: str, value: Any):
    #     await self.cache.set(key, value, self.expired_time)
