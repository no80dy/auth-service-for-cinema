import sys
import time
import redis
import backoff
import requests

from redis import Redis
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from tests.functional.settings import test_settings
from tests.functional.logger import logger


BACKOFF_MAX_TIME = 60

if __name__ == '__main__':
	redis_client = Redis(
		host=test_settings.REDIS_HOST, port=test_settings.REDIS_PORT
	)

	@backoff.on_exception(
		backoff.expo,
		(redis.exceptions.ConnectionError, ),
		max_time=BACKOFF_MAX_TIME
	)
	def check_redis_readiness():
		while True:
			if redis_client.ping():
				logger.info('Redis ping OK')
				break
			time.sleep(1)

	try:
		check_redis_readiness()
	except ConnectionError:
		logger.info('Redis is not available')
		raise ConnectionError
