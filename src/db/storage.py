from .redis import RedisStorage


nosql_storage: RedisStorage | None = None


async def get_nosql_storage() -> RedisStorage:
	return nosql_storage
