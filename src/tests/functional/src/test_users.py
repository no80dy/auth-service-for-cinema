import pytest


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
