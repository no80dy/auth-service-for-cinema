from abc import ABC, abstractmethod
from typing import Any

from redis.asyncio import Redis


class INoSQLStorage(ABC):
	@abstractmethod
	async def get(self, key: str) -> str | None:
		pass

	@abstractmethod
	async def set(self, key: str, value: Any, expired_time: int) -> None:
		pass


class RedisStorage(INoSQLStorage):
	def __init__(self, **kwargs) -> None:
		self.connection = Redis(**kwargs)

	async def close(self):
		await self.connection.close()

	async def get(self, key: str) -> str | None:
		return await self.connection.get(key)

	async def set(self, key: str, value: Any, expired_time: int) -> None:
		await self.connection.set(key, value, expired_time)
