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
    group_name: str= Field(..., max_length=50)
    permissions: list[str]


class GroupUpdate(BaseModel):
    group_name: str
    permissions: list[str]


class GroupAssign(BaseModel):
    group_id: UUID


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
    groups: list[UUID]

    class Config:
        from_attributes = True
