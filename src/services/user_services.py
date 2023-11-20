from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from db.redis import RedisStorage
from db.storage import get_nosql_storage, TokenHandler
from models.entity import User

CACHE_EXPIRE_IN_SECONDS = 5 * 60  # 5 min


class UserService:
    def __init__(
        self,
        token_handler: TokenHandler,
        db: AsyncSession,
    ) -> None:
        self.token_handler = token_handler
        self.db = db

    async def check_exist_user(self, user_dto):
        result = await self.db.execute(select(User).where(User.username == user_dto.get('username')))
        user = result.scalars().first()

        return True if user else False

    async def check_unique_email(self, user_dto):
        result = await self.db.execute(select(User).where(User.email == user_dto.get('email')))
        user = result.scalars().first()

        return True if not user else False

    async def create_user(self, user_dto):
        user = User(**user_dto)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_user_by_username(self, username: str) -> User:
        try:
            result = await self.db.execute(select(User).where(User.login == username))

@lru_cache()
def get_user_service(
    no_sql: RedisStorage = Depends(get_nosql_storage),
    db: AsyncSession = Depends(get_session),
) -> UserService:
    token_handler = TokenHandler(no_sql, CACHE_EXPIRE_IN_SECONDS)

    return UserService(token_handler, db)
