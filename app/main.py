import uvicorn
import logging

from elasticsearch import AsyncElasticsearch
from fastapi.responses import ORJSONResponse
from fastapi import FastAPI
from redis.asyncio import Redis
from contextlib import asynccontextmanager

from app.api.v1 import films, genres, persons
from app.core import config
from app.core.logger import LOGGING
from app.db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        hosts=[f'http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}']
    )

    yield

    await redis.redis.close()
    await elastic.es.close()

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
