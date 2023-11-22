import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import select

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
				'group_name': 'admin',
				'permissions': ['create', 'update']
			},
			{
				'group_name': 'admin',
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
	make_post_request,
	group_create,
	expected_response
):
	await write_groups_with_permissions_in_database(
		['admin', 'guest', 'subscriber'], ['create', 'update']
	)

	result = await make_post_request('groups/', group_create)

	assert result['body']['group_name'] == expected_response['group_name']
	assert result['body']['permissions'] == expected_response['permissions']


@pytest.mark.parametrize(
	'group_create, expected_response',
	[
		(
			{
				'group_name': 'superuser',
			 	'permissions': []
			},
			{
				'status': HTTP_200
			}
		),
		(
			{
				'group_name': 'admin',
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
	make_post_request,
	group_create,
	expected_response
):
	await write_groups_with_permissions_in_database(
		['admin', 'guest', 'subscriber'], ['create', 'update']
	)
	result = await make_post_request('groups/', group_create)

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
				'length': 3
			}
		),
		(
			{
				'groups_names': [],
				'permissions_names': []
			},
			{
				'status': HTTP_200,
				'length': 0
			}
		),
	]
)
async def test_read_groups_positive(
	write_groups_with_permissions_in_database,
	make_get_request,
	database_request_data,
	expected_response
):
	await write_groups_with_permissions_in_database(
		database_request_data['groups_names'],
		database_request_data['permissions_names']
	)
	result = await make_get_request('groups/', {})

	assert len(result['body']) == expected_response['length']
	assert result['status'] == expected_response['status']


# @pytest.mark.parametrize(
# 	'group_update, expected_response',
# 	[
# 		(
# 			{
# 				'group_name': 'admin',
# 				'permissions': []
# 			},
# 			{
# 				'status': HTTP_200,
# 				'group_name': ''
# 			}
# 		)
# 	]
# )
# async def test_update_group(
# 	wtite_permissions_in_database,
# 	make_put_request,
# 	init_session,
# 	group_update,
# 	expected_response
# ):
# 	await wtite_permissions_in_database()
#
# 	group = Group('guest', permissions)
# 	init_session.add(group)
# 	await init_session.commit()
# 	await init_session.refresh(group)
#
# 	result = await make_put_request(f'groups/{group.id}', group_update)
#

