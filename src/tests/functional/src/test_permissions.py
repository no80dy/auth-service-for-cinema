import uuid

import pytest


HTTP_200 = 200
HTTP_404 = 404
HTTP_422 = 422
HTTP_409 = 409


@pytest.mark.parametrize(
	'permission_create, expected_response',
	[
		(
			{'permission_name': 'new_permission'},
			{
				'status': HTTP_200,
				'body': {'permission_name': 'new_permission'}
			}
		)
	]
)
async def test_create_permission(
	create_superuser,
	make_post_request,
	permission_create,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	result = await make_post_request(
		'permissions/',
		permission_create,
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']
	assert result['body']['permission_name'] == expected_response['body']['permission_name']


@pytest.mark.parametrize(
	'permission_create, expected_response',
	[
		(
			{'permission_name': 'new_permission'},
			{
				'status': HTTP_409
			}
		)
	]
)
async def test_create_permission_duplicate(
	create_superuser,
	make_post_request,
	permission_create,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	await make_post_request(
		'permissions/', permission_create, {'Authorization': f'Bearer {access_token}'}
	)
	result = await make_post_request(
		'permissions/', permission_create, {'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']


@pytest.mark.parametrize(
	'permission_create, expected_response',
	[
		(
			{'permission_name': None},
			{'status': HTTP_422}
		),
		(

			{'permission_name': 1234},
			{'status': HTTP_422}
		)
	]
)
async def test_permission_validation(
	create_superuser,
	make_post_request,
	permission_create,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	result = await make_post_request(
		'permissions/', permission_create, {'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']


@pytest.mark.parametrize(
	'permission_read, expected_response',
	[
		(
			{'permissions_count': 20},
			{
				'status': 200,
				'length': 21
			}
		),
		(
			{'permissions_count': 10},
			{
				'status': 200,
				'length': 11
			}
		)
	]
)
async def test_permissions_read(
	create_superuser,
	make_get_request,
	make_post_request,
	permission_read,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(f'users/signin', {'username': 'superuser', 'password': 'password123'})
	access_token = result['body']['access_token']

	for index in range(permission_read['permissions_count']):
		await make_post_request(
			'permissions/',
			{'permission_name': f'new_permission_{index}'},
			{'Authorization': f'Bearer {access_token}'}
		)

	result = await make_get_request('permissions/', {}, {'Authorization': f'Bearer {access_token}'})

	assert result['status'] == expected_response['status']
	assert len(result['body']) == expected_response['length']


@pytest.mark.parametrize(
	'permission_update, expected_response',
	[
		(
			{'permission_name': 'new_permission'},
			{
				'status': HTTP_200,
				'body': {'permission_name': 'new_permission'}
			}
		)
	]
)
async def test_permission_update(
	create_superuser,
	make_post_request,
	make_put_request,
	permission_update,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(
		f'users/signin',
		{'username': 'superuser', 'password': 'password123'}
	)
	access_token = result['body']['access_token']

	created_permission = await make_post_request(
		'permissions/',
		{'permission_name': 'new_permission'},
		{'Authorization': f'Bearer {access_token}'}
	)

	permission_id = created_permission['body']['id']
	result = await make_put_request(
		f'permissions/{permission_id}',
		{'permission_name': f'new_permission'},
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']
	assert result['body']['id'] == permission_id
	assert result['body']['permission_name'] == expected_response['body']['permission_name']


@pytest.mark.parametrize(
	'permission_update, expected_response',
	[
		(
			{'permission_name': 'new_permission'},
			{
				'status': HTTP_409
			}
		)
	]
)
async def test_permission_update_duplicates(
	create_superuser,
	make_post_request,
	make_put_request,
	permission_update,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(
		f'users/signin',
		{'username': 'superuser', 'password': 'password123'}
	)
	access_token = result['body']['access_token']

	await make_post_request(
		'permissions/',
		{'permission_name': 'new_permission'},
		{'Authorization': f'Bearer {access_token}'}
	)

	created_permission = await make_post_request(
		'permissions/',
		{'permission_name': 'old_permission'},
		{'Authorization': f'Bearer {access_token}'}
	)

	permission_id = created_permission['body']['id']
	result = await make_put_request(
		f'permissions/{permission_id}',
		{'permission_name': f'new_permission'},
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']


@pytest.mark.parametrize(
	'permission_update, expected_response',
	[
		(
			{'permission_name': None},
			{'status': HTTP_422}
		),
		(
			{'permission_name': 12345},
			{'status': HTTP_422}
		),
	]
)
async def test_permission_update_validation(
	create_superuser,
	make_post_request,
	make_put_request,
	permission_update,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(
		f'users/signin',
		{'username': 'superuser', 'password': 'password123'}
	)
	access_token = result['body']['access_token']

	created_permission = await make_post_request(
		'permissions/',
		{'permission_name': 'old_permission'},
		{'Authorization': f'Bearer {access_token}'}
	)

	permission_id = created_permission['body']['id']
	result = await make_put_request(
		f'permissions/{permission_id}',
		permission_update,
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']


@pytest.mark.parametrize(
	'permission_update, expected_response',
	[
		(
			{'permission_name': 'new_permission'},
			{'status': HTTP_404}
		)
	]
)
async def test_permission_update_does_not_exists(
	create_superuser,
	make_post_request,
	make_put_request,
	permission_update,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(
		f'users/signin',
		{'username': 'superuser', 'password': 'password123'}
	)
	access_token = result['body']['access_token']

	result = await make_put_request(
		f'permissions/{uuid.uuid4()}',
		permission_update,
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']


@pytest.mark.parametrize(
	'permission_delete, expected_response',
	[
		(
			{'permission_name': 'new_permission'},
			{
				'status': HTTP_200,
				'content': 'deleted successfully'
			}
		)
	]
)
async def test_permission_delete(
	create_superuser,
	make_post_request,
	make_delete_request,
	permission_delete,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(
		f'users/signin',
		{'username': 'superuser', 'password': 'password123'}
	)
	access_token = result['body']['access_token']

	created_permission = await make_post_request(
		'permissions/',
		{'permission_name': permission_delete['permission_name']},
		{'Authorization': f'Bearer {access_token}'}
	)

	permission_id = created_permission['body']['id']
	result = await make_delete_request(
		f'permissions/{permission_id}',
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']
	assert result['body'] == expected_response['content']


@pytest.mark.parametrize(
	'expected_response',
	[
		(
			{'status': HTTP_404}
		)
	]
)
async def test_permission_delete_does_not_exists(
	create_superuser,
	make_post_request,
	make_delete_request,
	expected_response
):
	await create_superuser('superuser', 'password123')
	result = await make_post_request(
		f'users/signin',
		{'username': 'superuser', 'password': 'password123'}
	)
	access_token = result['body']['access_token']

	result = await make_delete_request(
		f'permissions/{uuid.uuid4()}',
		{'Authorization': f'Bearer {access_token}'}
	)

	assert result['status'] == expected_response['status']
