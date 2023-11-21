# from functools import lru_cache
#
# from fastapi import Depends, FastAPI, HTTPException, Request
# from fastapi.responses import JSONResponse
# from sqlalchemy.ext.asyncio import AsyncSession
# from async_fastapi_jwt_auth import AuthJWT
#
# from db.storage import get_nosql_storage
# from models.entity import User
# from core.config import JWTSettings
#
#
# @AuthJWT.load_config
# def get_config():
#     return JWTSettings()
#
#
# class AuthService:
#     def __init__(
#             self,
#             cache_handler: CacheUserHandler,
#             db: AsyncSession,
#     ) -> None:
#         self.cache_handler = cache_handler
#         self.db = db
#
#     async def create_pair_tokens(
#         self,
#         user: User,
#         Authorize: AuthJWT = Depends()
#     ) -> dict[str, str]:
#         """Создает пару access и refresh токенов"""
#         access_token = await Authorize.create_access_token(subject=user.username)
#         refresh_token = await Authorize.create_refresh_token(subject=user.username)
#
#         return {"access_token": access_token, "refresh_token": refresh_token}
#
#     async def set_tokens_cookies(
#         self,
#         tokens
#     ):
#         # Set the JWT cookies in the response
#         await Authorize.set_access_cookies(access_token)
#         await Authorize.set_refresh_cookies(refresh_token)
#
# @lru_cache()
# def get_auth_service(
#     cache: ICache = Depends(get_cache),
#     elastic: ElasticStorage = Depends(get_elastic),
# ) -> AuthService:
#     cache_handler = CachePersonHandler(cache, PERSON_CACHE_EXPIRE_IN_SECONDS)
#     storage_handler = ElasticPersonHandler(elastic)
#
#     return AuthService(cache_handler, storage_handler)