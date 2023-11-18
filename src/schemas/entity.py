from uuid import UUID

from pydantic import BaseModel


class PermissionInDB(BaseModel):
    id: UUID
    permission_name: str


class PermissionCreate(BaseModel):
    permission_name: str


class PermissionRead(BaseModel):
    permission_name: str


class GroupInDB(BaseModel):
    id: UUID
    group_name: str
    permissions: list[PermissionInDB]


class GroupCreate(BaseModel):
    group_name: str
    permissions: list[UUID]

class GroupRead(BaseModel):
    id: UUID
    group_name: str
    permissions: list[PermissionInDB]


class GroupUpdate(BaseModel):
    group_name: str
    permissions: list[UUID]


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
