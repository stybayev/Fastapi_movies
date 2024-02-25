import logging

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

from app.api.v1 import films
from app.core import config
from app.core.logger import LOGGING
from app.db import elastic, redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

#
# @app.on_event("startup")
# async def startup():
#     # Подключаемся к базам при старте сервера
#     # Подключиться можем при работающем event-loop
#     # Поэтому логика подключения происходит в асинхронной функции
#     redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
#     elastic.es = AsyncElasticsearch(
#         hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"]
#     )
#
#
# @app.on_event("shutdown")
# async def shutdown():
#     # Отключаемся от баз при выключении сервера
#     await redis.redis.close()
#     await elastic.es.close()
#
#
# # Подключаем роутер к серверу, указав префикс /v1/films
# # Теги указываем для удобства навигации по документации
# app.include_router(films.router, prefix="/api/v1/films", tags=["films"])


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


# Don't do this in production!
@app.post("/user/")
async def create_user(user: UserIn) -> UserIn:
    return user
