import uuid
from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base


groups_users_table = Table(
	'groups_users',
	Base.metadata,
	Column('group_id', ForeignKey('groups.id')),
	Column('user_id', ForeignKey('users.id'))
)

groups_permissions_table = Table(
	'groups_permissions',
	Base.metadata,
	Column('group_id', ForeignKey('groups.id')),
	Column('permission_id', ForeignKey('permissions.id'))
)


class Permission(Base):
	__tablename__ = 'permissions'

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
	permission_name = Column(String(50), unique=True, nullable=False)


class Group(Base):
	__tablename__ = 'groups'

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
	group_name = Column(String(50), nullable=False)
	permissions = relationship(
		'Permission',
		secondary=groups_permissions_table,
		lazy='joined'
	)

	def __init__(self, group_name: str, permissions: list[Permission]):
		self.group_name = group_name
		self.permissions = permissions


class User(Base):
	__tablename__ = 'users'

	id = Column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
		unique=True,
		nullable=False
	)
	login = Column(String(255), unique=True, nullable=False)
	password = Column(String(255), nullable=False)
	first_name = Column(String(50))
	last_name = Column(String(50))
	created_at = Column(DateTime, default=datetime.utcnow)

	groups = relationship('Group', secondary=groups_users_table)

	def __init__(
		self,
		login: str,
		password: str,
		first_name: str,
		last_name: str
	) -> None:
		self.login = login
		self.password = self.password = generate_password_hash(password)
		self.first_name = first_name
		self.last_name = last_name

	def check_password(self, password: str) -> bool:
		return check_password_hash(self.password, password)

	def __repr__(self) -> str:
		return f'<User {self.login}>'
