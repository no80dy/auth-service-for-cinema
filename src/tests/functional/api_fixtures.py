import aiohttp
import pytest_asyncio

from .settings import test_settings


@pytest_asyncio.fixture(scope='session')
async def fastapi_session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture(scope='function')
def make_get_request(fastapi_session: aiohttp.ClientSession):
    async def inner(endpoint: str, query_data: dict, headers: dict | None = None):
        url = test_settings.SERVICE_URL + f'/api/v1/{endpoint}'
        async with fastapi_session.get(url, params=query_data, headers=headers) as response:
            body = await response.json() if response.headers['Content-type'] == 'application/json' else await response.text()
            headers = response.headers
            status = response.status

            response = {
                'body': body,
                'headers': headers,
                'status': status
            }
            return response
    return inner


@pytest_asyncio.fixture(scope='function')
def make_post_request(fastapi_session: aiohttp.ClientSession):
    async def inner(endpoint: str, body: dict | None = None, headers: dict | None = None):
        url = test_settings.SERVICE_URL + f'/api/v1/{endpoint}'
        async with fastapi_session.post(url, json=body, headers=headers) as response:
            body = await response.json() \
                if response.headers['Content-type'] == 'application/json' else response.text()

            headers, status = response.headers, response.status
            response = {
                'body': body,
                'headers': headers,
                'status': status
            }
            return response
    return inner


@pytest_asyncio.fixture(scope='function')
def make_put_request(fastapi_session: aiohttp.ClientSession):
    async def inner(endpoint: str, body: dict, headers: dict | None = None):
        url = test_settings.SERVICE_URL + f'/api/v1/{endpoint}'
        async with fastapi_session.put(url, json=body, headers=headers) as response:
            body = await response.json() if response.headers['Content-type'] == 'application/json' else response.text()
            headers, status = response.headers, response.status
            response = {
                'body': body,
                'headers': headers,
                'status': status
            }
            return response
    return inner


@pytest_asyncio.fixture(scope='function')
def make_delete_request(fastapi_session: aiohttp.ClientSession):
    async def inner(endpoint: str, headers: dict | None = None):
        url = test_settings.SERVICE_URL + f'/api/v1/{endpoint}'
        async with fastapi_session.delete(
            url,
            headers=headers
        ) as response:
            body = await response.json() if response.headers['Content-type'] == 'application/json' else response.text()
            headers, status = response.headers, response.status
            response = {
                'body': body,
                'headers': headers,
                'status': status
            }
            return response

    return inner
