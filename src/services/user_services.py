import logging
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from db.redis import RedisStorage
from db.storage import get_nosql_storage, TokenHandler
from models.entity import User, RefreshSession, UserLoginHistory
from schemas.entity import RefreshToDb, UserLoginHistoryInDb, UserLogoutHistoryInDb, RefreshDelDb


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

    async def get_user_by_username(self, username: str) -> User | None:
        """Возвращает пользователя из базы данных по его username, если он есть."""
        try:
            result = await self.db.execute(select(User).where(User.username == username))
            user = result.scalars().first()
            return user
        except Exception as e:
            logging.error(e)

    async def put_refresh_session_in_db(self, data: RefreshToDb) -> None:
        """Записывает созданный refresh токен в базу данных."""
        try:
            row = RefreshSession(**data.model_dump())
            self.db.add(row)
            await self.db.commit()
            await self.db.refresh(row)
        except Exception as e:
            logging.error(e)

    async def del_refresh_session_in_db(self, data: RefreshDelDb) -> None:
        """Помечает refresh токен как удаленный в базе данных."""
        try:
            stmt = update(RefreshSession). \
                values(is_active=False). \
                where(User.id == data.user_id and RefreshSession.user_agent == data.user_agent)

            await self.db.execute(stmt)
            await self.db.commit()
        except Exception as e:
            logging.error(e)

    async def put_login_history_in_db(self, data: UserLoginHistoryInDb) -> None:
        """Записывает историю входа в аккаунт в базу данных."""
        try:
            row = UserLoginHistory(**data.model_dump())

            self.db.add(row)
            await self.db.commit()
            await self.db.refresh(row)
        except Exception as e:
            logging.error(e)

    async def put_logout_history_in_db(self, data: UserLogoutHistoryInDb) -> None:
        """Записывает историю выхода из аккаунта в базу данных."""
        try:
            stmt = update(UserLoginHistory). \
                values(logout_at=data.logout_at). \
                where(User.id == data.user_id and UserLoginHistory.user_agent == data.user_agent)

            await self.db.execute(stmt)
            await self.db.commit()
        except Exception as e:
            logging.error(e)


@lru_cache()
def get_user_service(
    no_sql: RedisStorage = Depends(get_nosql_storage),
    db: AsyncSession = Depends(get_session),
) -> UserService:
    token_handler = TokenHandler(no_sql, CACHE_EXPIRE_IN_SECONDS)

    return UserService(token_handler, db)
