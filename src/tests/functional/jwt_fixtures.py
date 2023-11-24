from datetime import timedelta

import pytest_asyncio
from pydantic import BaseModel
from async_fastapi_jwt_auth import AuthJWT


class JWTSettings(BaseModel):
    authjwt_secret_key: str = 'secret'
    # Хранить и получать JWT токены из заголовков
    authjwt_token_location: set = {'headers'}
    authjwt_header_name: str = 'Authorization'
    authjwt_header_type: str = 'Bearer'
    authjwt_access_token_expires: int = timedelta(minutes=10)
    authjwt_refresh_token_expires: int = timedelta(days=10)
    authjwt_cookie_csrf_protect: bool = False


@AuthJWT.load_config
def get_config():
    return JWTSettings()


@pytest_asyncio.fixture(scope='function')
async def create_fake_tokens():
    async def inner(user_id: str, username: str) -> dict:
        authorize = AuthJWT()
        user_claims = {'user_id': user_id}
        fake_access_token = await authorize.create_access_token(subject=username, user_claims=user_claims)
        fake_decrypted_access_token = await authorize.get_raw_jwt(fake_access_token)
        fake_refresh_token = await authorize.create_refresh_token(subject=username, user_claims=user_claims)
        fake_decrypted_refresh_token = await authorize.get_raw_jwt(fake_refresh_token)

        return {
            'access_token': fake_access_token,
            'decrypted_access_token': fake_decrypted_access_token,
            'refresh_token': fake_refresh_token,
            'decrypted_refresh_token': fake_decrypted_refresh_token,
        }

    return inner
