import sys
import uuid
from pathlib import Path
from sqlalchemy import select

sys.path.append(str(Path(__file__).resolve().parents[3]))

from models.entity import User

async def test_postgres_connections(
	make_get_request,
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
