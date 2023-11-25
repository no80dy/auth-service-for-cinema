from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from async_fastapi_jwt_auth.exceptions import AuthJWTException

from api.v1 import users, groups, permissions

from core.config import settings

from db import storage
from db.redis import RedisStorage


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.nosql_storage = RedisStorage(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        decode_responses=True
    )
    yield
    await storage.nosql_storage.close()


app = FastAPI(
    description='Сервис по авторизации и аутентификации пользователей',
    version='1.0.0',
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=JSONResponse,
    lifespan=lifespan
)

app.include_router(users.router, prefix='/api/v1/users', tags=['users'])
app.include_router(groups.router, prefix='/api/v1/groups', tags=['groups'])
app.include_router(permissions.router, prefix='/api/v1/permissions', tags=['permissios'])


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    """Exception handler for authjwt."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )
