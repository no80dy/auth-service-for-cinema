from abc import ABC

from redis.asyncio import Redis


class INoSQLStorage(ABC):
	pass


class RedisStorage(INoSQLStorage):
	def __init__(self, **kwargs) -> None:
		self.connection = Redis(**kwargs)

	async def close(self):
		await self.connection.close()
