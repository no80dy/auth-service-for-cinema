from http import HTTPStatus

import pytest
from datetime import datetime
from http import HTTPStatus

from models.entity import User, RefreshSession, UserLoginHistory


@pytest.mark.parametrize(
    'user_data, expected_response, status_code',
    [
        (
                {
                    "username": "string",
                    "password": "stringst",
                    "repeated_password": "stringst",
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
                HTTPStatus.CREATED,
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
                    "repeated_password": "stringst",
                    "first_name": "string",
                    "last_name": "string",
                    "email": "string"
                },
                {
                    "detail": "Некорректное имя пользователя или пароль",
                },
                HTTPStatus.BAD_REQUEST,
        ),
        (
                {
                    "username": "string1",
                    "password": "stringst",
                    "repeated_password": "stringst",
                    "first_name": "string",
                    "last_name": "string",
                    "email": "string"  # попытка создать юзера с уже существующим в БД email
                },
                {
                    "detail": "Пользователь с данным email уже зарегистрирован",
                },
                HTTPStatus.BAD_REQUEST,
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
        "repeated_password": "stringst",
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
                    "username": "string",  # попытка создать юзера с уже существующим в БД username
                    "password": "stringst",
                    "repeated_old_password": "stringst",
                    "new_password": "new_password",
                },
                {
                    "username": "string"
                },
                HTTPStatus.OK,
        ),
        (
                {
                    "username": "string",
                    "password": "stringst",
                    "repeated_old_password": "stringst_dont_right",  # несовпадающий пароль
                    "new_password": "new_password",
                },
                {
                    "detail": "Введены некорректные данные",
                },
                HTTPStatus.BAD_REQUEST,
        ),
        (
                {
                    "username": "string",
                    "password": "stringst",
                    "repeated_old_password": "stringst",
                    "new_password": "stringst",  # новый пароль совпадает со старым
                },
                {
                    "detail": "Введены некорректные данные",
                },
                HTTPStatus.BAD_REQUEST,
        ),
    ]
)
async def test_change_password_user(
    make_post_request,
    user_data,
    expected_response,
    status_code,
):
    first_user = {
        "username": "string",
        "password": "stringst",
        "repeated_password": "stringst",
        "first_name": "string",
        "last_name": "string",
        "email": "string"
    }
    await make_post_request('users/signup', first_user)

    result = await make_post_request('users/change_password', user_data)

    assert result.get('body') == expected_response
    assert result.get('status') == status_code


@pytest.mark.parametrize(
    'expected_response, status_code',
    [
        (
                [],
                HTTPStatus.OK,
        ),
    ]
)
async def test_get_history_user_empty(
    make_post_request,
    make_get_request,
    expected_response,
    status_code,
):
    first_user = {
        "username": "string",
        "password": "stringst",
        "repeated_password": "stringst",
        "first_name": "string",
        "last_name": "string",
        "email": "string"
    }
    created_user = await make_post_request('users/signup', first_user)
    user_id = created_user.get('body').get('id')
    result = await make_get_request(f'users/{user_id}/get_history', {})

    assert result.get('body').get('items') == expected_response
    assert result.get('status') == status_code


async def test_get_one_history_user(
    make_post_request,
    make_get_request,
):
    first_user = {
        "username": "string",
        "password": "stringst",
        "repeated_password": "stringst",
        "first_name": "string",
        "last_name": "string",
        "email": "string"
    }
    signin_data = {
        "username": "string",
        "password": "stringst",
    }
    created_user = await make_post_request('users/signup', first_user)
    await make_post_request('users/signin', signin_data)

    user_id = created_user.get('body').get('id')

    result = await make_get_request(f'users/{user_id}/get_history', {})

    assert len(result.get('body').get('items')) == 1
    assert set(result.get('body').get('items')[0].keys()) == {'login_at', 'user_agent', 'user_id'}
    assert result.get('status') == HTTPStatus.OK


async def test_get_history_user(
    make_post_request,
    make_get_request,
    create_fake_login,
):
    fake_data = await create_fake_login()
    await make_post_request(
        'users/logout',
        headers={
            'Authorization': f'Bearer {fake_data["access_token"]}',
            'User-Agent': fake_data['user_agent'],
        }
    )
    signin_data = {
        "username": fake_data.get('user').username,
        "password": '123456789',
    }
    await make_post_request('users/signin', signin_data)
    result = await make_get_request(f'users/{fake_data.get("user").id}/get_history', {'page_size': 1})

    assert len(result.get('body').get('items')) == 1


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
        create_fake_login,
        make_post_request,
        expected_response,
        status_code,
):
    fake_data = await create_fake_login()
    result = await make_post_request(
        'users/logout',
        headers={
            'Authorization': f'Bearer {fake_data["access_token"]}',
            'User-Agent': fake_data['user_agent'],
        }
    )

    assert result.get('body').keys() == expected_response.keys()
    assert result.get('body') == expected_response
    assert result.get('status') == status_code


@pytest.mark.parametrize(
    'expected_response, status_code',
    [
        (
            {
                'detail': 'Only access tokens are allowed'
            },
            HTTPStatus.UNPROCESSABLE_ENTITY
        ),
    ]
)
async def test_negative1_logout_user(
        create_fake_login,
        make_post_request,
        expected_response,
        status_code,
):
    fake_data = await create_fake_login()
    result = await make_post_request(
        'users/logout',
        headers={
            'Authorization': f'Bearer {fake_data["refresh_token"]}',
            'User-Agent': fake_data['user_agent'],
        }
    )

    assert result.get('body').keys() == expected_response.keys()
    assert result.get('body') == expected_response
    assert result.get('status') == status_code


@pytest.mark.parametrize(
    'expected_response, status_code',
    [
        (
            {
                'detail': 'Not authenticated'
            },
            HTTPStatus.FORBIDDEN
        ),
    ]
)
async def test_negative2_logout_user(
        create_fake_login,
        make_post_request,
        expected_response,
        status_code,
):
    fake_data = await create_fake_login()
    result = await make_post_request(
        'users/logout',
        headers={
            'Authorization': '',
            'User-Agent': fake_data['user_agent'],
        }
    )

    assert result.get('body').keys() == expected_response.keys()
    assert result.get('body') == expected_response
    assert result.get('status') == status_code


@pytest.mark.parametrize(
    'expected_response, status_code',
    [
        (
            {
                'access_token': '',
                'refresh_token': '',
            },
            HTTPStatus.OK
        ),
    ]
)
async def test_refresh_tokens(
        create_fake_login,
        make_post_request,
        expected_response,
        status_code,
):
    fake_data = await create_fake_login()
    result = await make_post_request(
        'users/refresh-tokens',
        headers={
            'Authorization': f'Bearer {fake_data["refresh_token"]}',
            'User-Agent': fake_data['user_agent'],
        }
    )

    assert result.get('body').keys() == expected_response.keys()
    assert result.get('status') == status_code


@pytest.mark.parametrize(
    'expected_response, status_code',
    [
        (
            {
                'detail': 'Only refresh tokens are allowed',
            },
            HTTPStatus.UNPROCESSABLE_ENTITY
        ),
    ]
)
async def test_negative_refresh_tokens(
        create_fake_login,
        make_post_request,
        expected_response,
        status_code,
):
    fake_data = await create_fake_login()
    result = await make_post_request(
        'users/refresh-tokens',
        headers={
            'Authorization': f'Bearer {fake_data["access_token"]}',
            'User-Agent': fake_data['user_agent'],
        }
    )

    assert result.get('body').keys() == expected_response.keys()
    assert result.get('status') == status_code
