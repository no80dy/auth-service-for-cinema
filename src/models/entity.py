import uuid
from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.types import String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base


class User(Base):
	__tablename__ = 'users'

	id = Column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
		unique=True,
		nullable=False
	)
	username = Column(String(255), unique=True, nullable=False)
	email = Column(String(50), unique=True)
	password = Column(String(255), nullable=False)
	first_name = Column(String(50))
	last_name = Column(String(50))
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, nullable=True)
	refresh_sessions = relationship('RefreshSession', cascade="all, delete")
	user_login_history = relationship('UserLoginHistory', cascade="all, delete")

	def __init__(
		self,
		username: str,
		password: str,
		first_name: str,
		last_name: str,
		email: str,
	) -> None:
		self.username = username
		self.password = generate_password_hash(password)
		self.first_name = first_name
		self.last_name = last_name
		self.email = email

	def check_password(self, password: str) -> bool:
		return check_password_hash(self.password, password)

	def __repr__(self) -> str:
		return f'<User {self.username}>'


class RefreshSession(Base):
	"""Модель хранения refresh токенов в postgres."""
	__tablename__ = 'refresh_sessions'

	id = Column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
		unique=True,
		nullable=False
	)

	user_id = Column(UUID, ForeignKey('users.id'))
	refresh_token = Column(String, nullable=False)
	user_agent = Column(String(255), nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	expired_at = Column(DateTime, nullable=False)
	is_active = Column(Boolean, unique=False, nullable=False, default=True)

	def __init__(
		self,
		user_id: UUID,
		refresh_token: str,
		user_agent: str,
		expired_at: datetime,
		is_active: bool
	) -> None:
		self.user_id = user_id
		self.refresh_token = refresh_token
		self.user_agent = user_agent
		self.expired_at = expired_at
		self.is_active = is_active

	def __repr__(self) -> str:
		return f'<User: {self.username} Token: {self.refresh_token} SignIn: {self.created_at}>'


class UserLoginHistory(Base):
	"""Модель хранения истории входов и выходов из аккаунта пользователя."""
	__tablename__ = 'user_login_history'

	id = Column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
		unique=True,
		nullable=False
	)

	user_id = Column(UUID, ForeignKey('users.id'))
	user_agent = Column(String(255), nullable=False)
	login_at = Column(DateTime, nullable=False, default=datetime.utcnow)
	logout_at = Column(DateTime, nullable=True, default=None)

	def __init__(
		self,
		user_id: UUID,
		user_agent: str,
		logout_at: datetime | None = None
	) -> None:
		self.user_id = user_id
		self.user_agent = user_agent
		self.logout_at = logout_at

	def __repr__(self) -> str:
		return f'<User: {self.username} U-A: {self.user_agent} SignIn: {self.login_at}>'