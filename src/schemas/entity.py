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