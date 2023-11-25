import sys
import asyncio
import pytest
import pytest_asyncio

from redis.asyncio import Redis

from .settings import test_settings


@pytest.fixture(scope="session")
def event_loop():
	try:
		loop = asyncio.get_running_loop()
	except RuntimeError:
		loop = asyncio.new_event_loop()
	yield loop
	loop.close()


@pytest_asyncio.fixture(scope='session')
async def redis_client() -> Redis:
	async with Redis(host=test_settings.redis_host, port=test_settings.redis_port) as client:
		yield client


pytest_plugins = [
	'tests.functional.api_fixtures',
	'tests.functional.postgres_fixtures',
	'tests.functional.jwt_fixtures',
]