import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import select

sys.path.append(str(Path(__file__).resolve().parents[3]))

from models.entity import User, Group, Permission


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
				'permissions': [
					'create', 'read', 'update', 'delete'
				]
			},
			{
				'group_name': 'admin',
				'permissions': [
					{'permission_name': 'create'},
					{'permission_name': 'read'},
					{'permission_name': 'update'},
					{'permission_name': 'delete'},
				]
			}
		)
	]
)
async def test_create_group(
	init_session,
	make_post_request,
	group_create,
	expected_response
):
	for permission_name in group_create['permissions']:
		init_session.add(Permission(permission_name))
	await init_session.commit()

	result = await make_post_request('groups/', group_create)

	assert result['body']['group_name'] == expected_response['group_name']
	assert result['body']['permissions'] == expected_response['permissions']
