from datetime import timedelta, datetime

import pytest_asyncio
from pydantic import BaseModel
from async_fastapi_jwt_auth import AuthJWT

from models.entity import User, RefreshSession, UserLoginHistory


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


@pytest_asyncio.fixture(scope='function')
async def create_fake_login(
        create_fake_tokens,
        create_fake_user_in_db,
        create_fake_history_in_db,
        create_fake_session_in_db
):
    async def inner() -> dict:
        fake_user_agent = 'fake-user-agent'
        fake_user = User(
            id='cf02ca78-9a5c-4d18-9ea9-682e1b0cc0da',
            username='fake-user',
            password='123456789',
            email='foo@example.com',
            first_name='Aliver',
            last_name='Stone'
        )
        await create_fake_user_in_db(fake_user)

        fake_user_history = UserLoginHistory(
            user_id=fake_user.id,
            user_agent=fake_user_agent,

        )
        await create_fake_history_in_db(fake_user_history)

        fake_tokens = await create_fake_tokens(str(fake_user.id), fake_user.username)
        fake_user_session = RefreshSession(
            user_id=fake_user.id,
            refresh_jti=fake_tokens['decrypted_refresh_token']['jti'],
            expired_at=datetime.fromtimestamp(fake_tokens['decrypted_refresh_token']['exp']),
            user_agent=fake_user_agent,
            is_active=True,
        )
        await create_fake_session_in_db(fake_user_session)

        return {
            'user': fake_user,
            'user_session': fake_user_session,
            'user_agent': fake_user_agent,
            'access_token': fake_tokens['access_token'],
            'refresh_token': fake_tokens['refresh_token'],

        }

    return inner
