import uuid
import pytest


HTTP_422 = 422
HTTP_404 = 404
HTTP_200 = 200


@pytest.mark.parametrize(
	'group_create, expected_response',
	[
		(
			{
				'group_name': 'new_group',
				'permissions': ['create', 'update', ]
			},
			{
				'status': HTTP_200,
				'body': {
					'group_name': 'new_group',
					'permissions': [
						{'permission_name': 'create'},
						{'permission_name': 'update'},
					]
				}
			}
		),
	]
)
async def test_create_group(
	create_superuser,
	make_post_request,
	group_create,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	for permission_name in group_create['permissions']:
		await make_post_request(
			'permissions/',
			{'permission_name': permission_name},
			{'Authorization': f'Bearer {access_token}'}
		)

	result = await make_post_request(
		'groups/',
		group_create,
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']
	assert result['body']['group_name'] == expected_response['body']['group_name']
	assert result['body']['permissions'] == expected_response['body']['permissions']


@pytest.mark.parametrize(
	'group_create, expected_response',
	[
		(
			{
				'group_name': 'new_group',
				'permissions': ['new_permission', ]
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
		),
		(
			{
				'group_name': 123,
				'permissions': []
			},
			{
				'status': HTTP_422
			}
		)
	]
)
async def test_create_group_with_incorrect_data(
	create_superuser,
	make_post_request,
	group_create,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	result = await make_post_request(
		'groups/',
		group_create,
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']


@pytest.mark.parametrize(
	'group_data, expected_response',
	[
		(
			{
				'groups': [
					{
						'group_name': f'new_group_{index}',
						'permissions': ['new_permission', ]
					}
					for index in range(20)
				],
			},
			{
				'status': HTTP_200,
				'length': 21
			}
		),
		(
			{
				'groups': [
					{
						'group_name': f'new_group_{index}',
						'permissions': 'new_permission'
					}
					for index in range(1)
				],
			},
			{
				'status': HTTP_200,
				'length': 1
			}
		),
	]
)
async def test_read_groups(
	create_superuser,
	make_post_request,
	make_get_request,
	group_data,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	for group in group_data['groups']:
		await make_post_request(
			'permissions/',
			{'permission_name': group['permissions'][0]},
			{'Authorization': f'Bearer {access_token}'}
		)

	for group in group_data['groups']:
		await make_post_request(
			'groups/',
			group,
			{'Authorization': f'Bearer {access_token}'}
		)

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
				'group_name': 'new_group',
				'permissions': ['create', ]
			},
			{
				'status': HTTP_200,
				'group_name': 'new_group',
				'permissions': [
					{'permission_name': 'create'},
				]
			}
		)
	]
)
async def test_update_group(
	make_post_request,
	create_superuser,
	make_put_request,
	group_update,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	for permission in group_update['permissions']:
		await make_post_request(
			'permissions/',
			{'permission_name': permission},
			{'Authorization': f'Bearer {access_token}'}
		)

	group = await make_post_request(
		'groups/',
		group_update,
		{'Authorization': f'Bearer {access_token}'}
	)

	group_id = group['body']['id']
	result = await make_put_request(
		f'groups/{group_id}',
		group_update,
		{'Authorization': f'Bearer {access_token}'}
	)
	assert result['body']['group_name'] == expected_response['group_name']
	assert result['body']['permissions'] == expected_response['permissions']


@pytest.mark.parametrize(
	'group_update, expected_response',
	[
		(
			{
				'group_name': 'new_group',
				'permissions': ['new_permission', ]
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
		),
		(
			{
				'group_name': 12345,
				'permissions': []
			},
			{
				'status': HTTP_422
			}
		)
	]
)
async def test_update_group_with_incorrect_data(
	create_superuser,
	make_post_request,
	make_put_request,
	group_update,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	group = await make_post_request(
		'groups/',
		{'group_name': 'old_group', 'permissions':  []},
		{'Authorization': f'Bearer {access_token}'}
	)

	group_id = group['body']['id']
	result = await make_put_request(
		f'groups/{group_id}',
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
				'permissions': []
			},
			{
				'status': HTTP_200,
				'content': 'deleted successfully'
			}
		)
	]
)
async def test_delete_group(
	create_superuser,
	make_post_request,
	make_delete_request,
	group_delete,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	group = await make_post_request(
		'groups/',
		group_delete,
		{'Authorization': f'Bearer {access_token}'}
	)

	group_id = group['body']['id']
	result = await make_delete_request(
		f'groups/{group_id}',
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
async def test_delete_group_does_not_exists(
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
