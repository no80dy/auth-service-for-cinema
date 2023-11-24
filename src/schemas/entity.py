from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PermissionDetailView(BaseModel):
    id: UUID
    permission_name: str


class PermissionShortView(BaseModel):
    permission_name: str


class PermissionCreate(BaseModel):
    permission_name: str = Field(..., max_length=50)


class PermissionUpdate(BaseModel):
    permission_name: str = Field(..., max_length=50)


class GroupDetailView(BaseModel):
    id: UUID
    group_name: str
    permissions: list[PermissionShortView]


class GroupShortView(BaseModel):
    group_name: str = Field(..., max_length=50)
    permissions: list[PermissionShortView]


class GroupCreate(BaseModel):
    group_name: str = Field(..., max_length=50)
    permissions: list[str]


class GroupUpdate(BaseModel):
    group_name: str
    permissions: list[str]


class GroupAssign(BaseModel):
    group_id: UUID


class UserSighIn(BaseModel):
    username: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)


class UserCreate(UserSighIn):
    repeated_password: str = Field(..., min_length=8, max_length=255)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: str = Field(..., max_length=50)


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    groups: list[UUID]

    class Config:
        from_attributes = True


class UserChangePassword(UserSighIn):
    repeated_old_password: str = Field(..., min_length=8, max_length=255)

    new_password: str = Field(..., min_length=8, max_length=255)


class UserResponseUsername(BaseModel):
    username: str = Field(..., max_length=255)


class RefreshToDb(BaseModel):
    """Модель записи сессии в postgres."""
    user_id: UUID
    refresh_jti: str
    user_agent: str = Field(max_length=255)
    expired_at: datetime
    is_active: bool


class RefreshDelDb(BaseModel):
    """Модель удаления сессии из postgres."""
    user_id: UUID
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


class UserResponseHistoryInDb(UserLoginHistoryInDb):
    login_at: datetime
