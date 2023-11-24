import pytest
from http import HTTPStatus

from models.entity import User, RefreshSession, UserLoginHistory


@pytest.mark.parametrize(
    'user_data, expected_response, status_code',
    [
        (
                {
                    "username": "string",
                    "password": "stringst",
                    "first_name": "string",
                    "last_name": "string",
                    "email": "string"
                },
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "first_name": "string",
                    "last_name": "string",
                    "groups": []
                },
                201
        ),
    ]
)
async def test_registrations_user(
        make_post_request,
        user_data,
        expected_response,
        status_code,
):
    result = await make_post_request('users/signup', user_data)

    assert result.get('body').keys() == expected_response.keys()

    result.get('body').pop('id')
    expected_response.pop('id')

    assert result.get('body') == expected_response
    assert result.get('status') == status_code


@pytest.mark.parametrize(
    'user_data, expected_response, status_code',
    [
        (
                {
                    "username": "string",  # попытка создать юзера с уже существующим в БД username
                    "password": "stringst",
                    "first_name": "string",
                    "last_name": "string",
                    "email": "string"
                },
                {
                    "detail": "Некорректное имя пользователя или пароль",
                },
                400
        ),
        (
                {
                    "username": "string1",
                    "password": "stringst",
                    "first_name": "string",
                    "last_name": "string",
                    "email": "string"  # попытка создать юзера с уже существующим в БД email
                },
                {
                    "detail": "Пользователь с данным email уже зарегистрирован",
                },
                400
        ),
    ]
)
async def test_negative_registrations_user(
        make_post_request,
        user_data,
        expected_response,
        status_code,
):
    first_user = {
        "username": "string",
        "password": "stringst",
        "first_name": "string",
        "last_name": "string",
        "email": "string"
    }
    await make_post_request('users/signup', first_user)

    result = await make_post_request('users/signup', user_data)

    assert result.get('body') == expected_response
    assert result.get('status') == status_code


@pytest.mark.parametrize(
    'user_data, expected_response, status_code',
    [
        (
                {
                    "username": "fake-user",
                    "password": "123456789",
                },
                {
                    'access_token': '',
                    'refresh_token': '',
                },
                HTTPStatus.OK
        ),
    ]
)
async def test_signin_user(
        create_fake_user_in_db,
        make_post_request,
        user_data,
        expected_response,
        status_code,
):
    fake_user = User(
        username='fake-user',
        password='123456789',
        email='foo@example.com',
        first_name='Aliver',
        last_name='Stone'
    )
    await create_fake_user_in_db(fake_user)
    result = await make_post_request('users/signin', user_data)

    assert result.get('body').keys() == expected_response.keys()
    assert result.get('status') == status_code


@pytest.mark.parametrize(
    'user_data, status_code',
    [
        (
                {
                    "username": "fake-user_no_exist",
                    "password": "123456789",
                },
                HTTPStatus.UNAUTHORIZED
        ),
        (
                {
                    "username": "fake-user",
                    "password": "123456789_no_exist",
                },
                HTTPStatus.UNAUTHORIZED
        ),
        (
                {
                    "password": "123456789_no_exist",
                },
                HTTPStatus.UNPROCESSABLE_ENTITY
        ),
        (
                {
                    "username": "fake-user",
                },
                HTTPStatus.UNPROCESSABLE_ENTITY
        ),
    ]
)
async def test_negative1_signin_user(
        create_fake_user_in_db,
        make_post_request,
        user_data,
        status_code,
):
    fake_user = User(
        username='fake-user',
        password='123456789',
        email='foo@example.com',
        first_name='Aliver',
        last_name='Stone'
    )
    await create_fake_user_in_db(fake_user)
    result = await make_post_request('users/signin', user_data)

    assert result.get('status') == status_code


@pytest.mark.parametrize(
    'user_data, expected_response, status_code',
    [
        (
                {
                    "username": "fake-user",
                    "password": "123456789",
                },
                {
                    "detail": "Данный пользователь уже совершил вход с данного устройства",
                },
                HTTPStatus.BAD_REQUEST,
        )
    ])
async def test_negative2_signin_user(
        create_fake_user_in_db,
        make_post_request,
        user_data,
        expected_response,
        status_code,
):
    fake_user = User(
        username='fake-user',
        password='123456789',
        email='foo@example.com',
        first_name='Aliver',
        last_name='Stone'
    )
    await create_fake_user_in_db(fake_user)

    await make_post_request('users/signin', user_data)
    result = await make_post_request('users/signin', user_data)

    assert result.get('body').keys() == expected_response.keys()
    assert result.get('body') == expected_response
    assert result.get('status') == status_code


@pytest.mark.parametrize(
    'expected_response, status_code',
    [
        (
            {
                'detail': 'Выход осуществлен успешно'
            },
            HTTPStatus.OK
        ),
    ]
)
async def test_logout_user(
        create_fake_tokens,
        create_fake_user_in_db,
        create_fake_session_in_db,
        create_fake_history_in_db,
        make_post_request,
        expected_response,
        status_code,
):
    # Подготовка окружения
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
        expired_at=fake_tokens['decrypted_refresh_token']['exp'],
        user_agent=fake_user_agent,
        is_active=True,
    )
    await create_fake_session_in_db(fake_user_session)

    result = await make_post_request(
        'users/logout',
        headers={
            'Authorization': f'Bearer {fake_tokens["access_token"]}',
            'User-Agent': fake_user_agent,
        }
    )

    assert result.get('body').keys() == expected_response.keys()
    assert result.get('body') == expected_response
    assert result.get('status') == status_code
