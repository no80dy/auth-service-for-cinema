from uuid import UUID

from pydantic import BaseModel


class PermissionInDB(BaseModel):
    id: UUID
    permission_name: str


class PermissionCreate(BaseModel):
    permission_name: str

class PermissionUpdate(BaseModel):
    permission_name: str


class PermissionName(BaseModel):
    permission_name: str


class GroupInDB(BaseModel):
    id: UUID
    group_name: str
    permissions: list[PermissionName]


class GroupCreate(BaseModel):
    group_name: str
    permissions: list[str]

class GroupRead(BaseModel):
    group_name: str
    permissions: list[PermissionName]


class GroupUpdate(BaseModel):
    group_name: str
    permissions: list[str]


class UserCreate(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str

class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
