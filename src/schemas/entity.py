from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: str = Field(..., max_length=50)


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class UserChangePassword(BaseModel):
    username: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    repeaded_old_password: str = Field(..., min_length=8, max_length=255)

    new_password: str = Field(..., min_length=8, max_length=255)


class UserResponseUsername(BaseModel):
    username: str = Field(..., max_length=255)


class UserSighIn(BaseModel):
    username: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)


class RefreshToDb(BaseModel):
    """Модель записи refresh токена в postgres."""
    user_id: UUID
    refresh_jti: str
    user_agent: str = Field(max_length=255)
    expired_at: datetime
    is_active: bool


class RefreshDelDb(BaseModel):
    """Модель удаления refresh токена из postgres."""
    user_id: UUID
    refresh_jti: str
    user_agent: str = Field(max_length=255)


class UserLoginHistoryInDb(BaseModel):
    """Модель записи истории входа в аккаунт."""
    user_id: UUID
    user_agent: str = Field(max_length=255)


class UserLogoutHistoryInDb(BaseModel):
    """Модель записи истории выхода из аккаунта."""
    user_id: UUID
    user_agent: str = Field(max_length=255)
    logout_at: datetime
