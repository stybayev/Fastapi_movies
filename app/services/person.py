import logging
from functools import lru_cache
from typing import List

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import ValidationError
from redis.asyncio import Redis

from app.db.elastic import get_elastic
from app.db.redis import get_redis
from app.models.persons import BasePersonModel
from app.models.film import Films
from app.services.base import BaseService

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonsService(BaseService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)
        self.model = BasePersonModel
        self.index_name = "persons"

    async def _person_from_cache(self, person_id: str) -> BasePersonModel | None:
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = BasePersonModel.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: BasePersonModel):
        await self.redis.set(person.id, person.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_films(self, person_id: str,
                        page_size: int = 10,
                        page_number: int = 1) -> List[Films]:

        offset = (page_number - 1) * page_size
        query_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {
                                    "bool": {
                                        "must": [
                                            {"match": {"actors.id": person_id}}
                                        ]
                                    }
                                }
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {
                                    "bool": {
                                        "must": [
                                            {"match": {"writers.id": person_id}}
                                        ]
                                    }
                                }
                            }
                        },
                        {
                            "match": {"director.id": person_id}
                        }
                    ]
                }
            },
            "from": offset,
            "size": page_size
        }

        try:
            response = await self.elastic.search(index='movies', body=query_body)
        except Exception as e:
            logging.error(f"Failed to fetch persons from Elasticsearch: {e}")
            return []

        films = []
        for hit in response['hits']['hits']:
            film_data = {
                "id": hit["_id"],
                "title": hit["_source"]["title"],
                "imdb_rating": hit["_source"].get("imdb_rating")
            }
            try:
                film = Films(**film_data)
                films.append(film)
            except ValidationError as e:
                logging.error(f"Error validating person data: {e}")
                continue

        return films

    async def search_person(self, query: str,
                            page_size: int = 10,
                            page_number: int = 1
                            ) -> list[BasePersonModel]:
        offset = (page_number - 1) * page_size
        search_body = {
            "from": offset,
            "size": page_size,
            "query": {
                "match_all": {}
            }
        }

        if query:
            search_body["query"] = {
                "multi_match": {
                    "query": query,
                    "fields": ["full_name"]
                }
            }

        try:
            response = await self.elastic.search(index=self.index_name, body=search_body)
        except Exception as e:
            logging.error(f"Failed to search persons in Elasticsearch: {e}")
            return []

        persons = []
        for hit in response['hits']['hits']:
            try:
                person = BasePersonModel(**hit['_source'])
                persons.append(person)
            except ValidationError as e:
                logging.error(f"Error validating person data: {e}")
                continue

        return persons

    async def get_persons(self) -> list[BasePersonModel]:
        pagination_params = self.pagination.get_pagination_params()
        search_body = {**pagination_params}

        try:
            response = await self.elastic.search(index=self.index_name, body=search_body)
        except Exception as e:
            logging.error(f"Failed to search persons in Elasticsearch: {e}")
            return []

        persons = []
        for hit in response['hits']['hits']:
            try:
                person = BasePersonModel(**hit['_source'])
                persons.append(person)
            except ValidationError as e:
                logging.error(f"Error validating person data: {e}")
                continue

        return persons


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> PersonsService:
    return PersonsService(redis, elastic)
