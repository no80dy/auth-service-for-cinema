from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.config import settings
from db.postgres import create_database
from db import redis
from api.v1 import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    from models.entity import User

    redis.nosql_storage = redis.RedisStorage(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        decode_responses=True
    )
    await create_database()

    yield

    await redis.nosql_storage.close()


app = FastAPI(
    description='Информация о фильмах, жанрах и людях, участвовавших в создании произведения',
    version='1.0.0',
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=JSONResponse,
    lifespan=lifespan
)


app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )