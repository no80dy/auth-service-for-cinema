import logging
import sys
import asyncpg
import asyncio
import backoff

from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from tests.functional.settings import test_settings
from tests.functional.logger import logger


BACKOFF_MAX_TIME = 60

if __name__ == '__main__':
	async def connect_to_postgres() -> asyncpg.connection.Connection:
		conn = await asyncpg.connect(
			user=test_settings.POSTGRES_USER,
			password=test_settings.POSTGRES_PASSWORD,
			host=test_settings.POSTGRES_HOST,
			port=test_settings.POSTGRES_PORT
		)
		return conn

	@backoff.on_exception(
		backoff.expo,
		(asyncpg.PostgresConnectionError, asyncpg.PostgresSyntaxError),
		max_time=BACKOFF_MAX_TIME
	)
	async def wait_for_postgres():
		conn = await connect_to_postgres()
		logger.info('PostgreSQL connect OK')
		await conn.close()

	asyncio.run(wait_for_postgres())
