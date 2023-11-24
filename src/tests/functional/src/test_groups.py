import sys
import uuid
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import select
from unittest.mock import MagicMock

sys.path.append(str(Path(__file__).resolve().parents[3]))

from models.entity import User, Group, Permission


HTTP_422 = 422
HTTP_404 = 404
HTTP_200 = 200


async def test_postgres_connections(
	init_session
):
	user = User(
		username='fake-user',
		password='123456789',
		email='foo@example.com',
		first_name='Aliver',
		last_name='Stone'
	)
	init_session.add(user)
	await init_session.commit()
	await init_session.refresh(user)

	users = (await init_session.execute(select(User))).unique().scalars().all()
	assert len(users) == 1


@pytest.mark.parametrize(
	'group_create, expected_response',
	[
		(
			{
				'group_name': 'new_group',
				'permissions': ['create', 'update']
			},
			{
				'group_name': 'new_group',
				'permissions': [
					{'permission_name': 'create'},
					{'permission_name': 'update'},
				]
			}
		),
	]
)
async def test_create_group_without_positive(
	write_groups_with_permissions_in_database,
	create_superuser,
	make_post_request,
	group_create,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	await write_groups_with_permissions_in_database(
		['admin', 'guest', 'subscriber'], ['create', 'update']
	)

	result = await make_post_request(
		'groups/',
		group_create,
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['body']['group_name'] == expected_response['group_name']
	assert result['body']['permissions'] == expected_response['permissions']


@pytest.mark.parametrize(
	'group_create, expected_response',
	[
		(
			{
				'group_name': 'new_group',
				'permissions': ['delete']
			},
			{
				'status': HTTP_404
			}
		),
		(
			{
				'group_name': None,
				'permissions': []
			},
			{
				'status': HTTP_422
			}
		)
	]
)
async def test_create_group_negative(
	write_groups_with_permissions_in_database,
	create_superuser,
	make_post_request,
	group_create,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	await write_groups_with_permissions_in_database(
		['admin', 'guest', 'subscriber'], ['create', 'update']
	)
	result = await make_post_request(
		'groups/',
		group_create,
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']


@pytest.mark.parametrize(
	'database_request_data, expected_response',
	[
		(
			{
				'groups_names': ['admin', 'guest', 'subscriber'],
				'permissions_names': ['create', 'update']
			},
			{
				'status': HTTP_200,
				'length': 4
			}
		),
		(
			{
				'groups_names': [],
				'permissions_names': []
			},
			{
				'status': HTTP_200,
				'length': 1 # Так как мы залогинены под ролью суперпользователя
			}
		),
	]
)
async def test_read_groups_positive(
	write_groups_with_permissions_in_database,
	create_superuser,
	make_post_request,
	make_get_request,
	database_request_data,
	expected_response
):
	await write_groups_with_permissions_in_database(
		database_request_data['groups_names'],
		database_request_data['permissions_names']
	)
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	result = await make_get_request(
		'groups/',
		{},
		{'Authorization': f'Bearer {access_token}'}
	)

	assert len(result['body']) == expected_response['length']
	assert result['status'] == expected_response['status']


@pytest.mark.parametrize(
	'group_update, expected_response',
	[
		(
			{
				'group_name': 'admin',
				'permissions': ['create', ]
			},
			{
				'status': HTTP_200,
				'group_name': 'admin',
				'permissions': [
					{'permission_name': 'create'},
				]
			}
		)
	]
)
async def test_update_group_positive(
	create_group_with_permissions,
	make_post_request,
	create_superuser,
	make_put_request,
	group_update,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	group = await create_group_with_permissions('new_group', ['add', 'create'])

	result = await make_put_request(
		f'groups/{group.id}',
		group_update,
		{'Authorization': f'Bearer {access_token}'}
	)
	print(result)
	assert result['body']['group_name'] == expected_response['group_name'], result
	assert result['body']['permissions'] == expected_response['permissions']


@pytest.mark.parametrize(
	'group_update, expected_response',
	[
		(
			{
				'group_name': 'new_group',
				'permissions': ['create', 'update', ]
			},
			{
				'status': HTTP_404
			}
		),
		(
			{
				'group_name': None,
				'permissions': ['create', 'update', ]
			},
			{
				'status': HTTP_422
			}
		)
	]
)
async def test_update_group_negative(
	create_superuser,
	make_post_request,
	make_put_request,
	group_update,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	result = await make_put_request(
		f'groups/{uuid.uuid4()}',
		group_update,
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']


@pytest.mark.parametrize(
	'group_delete, expected_response',
	[
		(
			{
				'group_name': 'new_group',
				'permissions': ['create', 'update', ]
			},
			{
				'status': HTTP_200,
				'content': 'deleted successfully'
			}
		)
	]
)
async def test_delete_group_posisive(
	create_superuser,
	create_group_with_permissions,
	make_post_request,
	make_delete_request,
	group_delete,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	group = await create_group_with_permissions(
		group_delete['group_name'],
		group_delete['permissions']
	)

	result = await make_delete_request(
		f'groups/{group.id}',
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']
	assert result['body'] == expected_response['content']


@pytest.mark.parametrize(
	'group_delete, expected_response',
	[
		(
			{
				'group_id': uuid.uuid4()
			},
			{
				'status': HTTP_404,
			}
		)
	]
)
async def test_delete_group_negative(
	create_superuser,
	make_post_request,
	make_delete_request,
	group_delete,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	group_id = group_delete['group_id']
	result = await make_delete_request(
		f'groups/{group_id}',
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']
