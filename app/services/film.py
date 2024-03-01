import logging
from functools import lru_cache
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from pydantic import ValidationError
from redis.asyncio import Redis

from app.db.elastic import get_elastic
from app.db.redis import get_redis
from app.models.film import Film, Films
from app.utils.pagination import Pagination
from app.services.base import BaseService

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService(BaseService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, pagination: Pagination):
        super().__init__(redis, elastic)
        self.model = Film
        self.index_name = "movies"
        self.pagination = pagination

    async def get_by_id(self, film_id: str) -> Film | None:
        """
        Получить фильм по id
        :param film_id:
        :return:
        """

        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._entity_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм в кеш
            await self._put_entity_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Film | None:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None

        doc_source = doc["_source"]

        # Получаем данные о режиссерах, используя выделенную функцию
        # doc_source['director'] = [doc_source.get('director', '')] if doc_source.get('director', '') else []
        director_names = doc_source.get('director', [])

        if director_names:
            prepared = {
                'uuid': director_names['id'],
                'full_name': director_names['name']
            }

            doc_source['director'] = [prepared]
        else:
            doc_source['director'] = []

        # Получаем данные о жанрах, используя выделенную функцию
        genre_names = doc_source.get('genre', [])
        if genre_names:
            genres_data = await self._get_genres_data(genre_names)
            doc_source['genre'] = genres_data
        else:
            doc_source['genre'] = []

        try:
            return Film(**doc_source)
        except ValidationError as e:
            logging.error(e)
            return None

    async def _film_from_cache(self, film_id: str) -> Film | None:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _get_genres_data(self, genre_names: list[str]) -> list[dict]:
        """
        Получить данные о жанрах
        :param genre_names:
        :return:
        """
        genres_data = []
        for genre_name in genre_names:
            try:
                response = await self.elastic.search(
                    index="genres",
                    body={
                        "query": {
                            "match": {
                                "name.raw": genre_name
                            }
                        }
                    }
                )
                for hit in response['hits']['hits']:
                    genre_source = hit["_source"]
                    genres_data.append({"name": genre_source["name"], "uuid": hit["_id"]})
            except NotFoundError:
                logging.error(f"Genre {genre_name} not found")
        return genres_data

    async def get_films(self, genre: str | None = None,
                        sort: str | None = None,
                        ) -> list[Films]:
        """
        Получить список фильмов с учетом жанра, сортировки, размера страницы и номера страницы.
        Возвращает список объектов Film.
        """
        pagination_params = self.pagination.get_pagination_params()
        query_body = {
            "query": {
                "bool": {
                    "must": []
                }
            },
            "sort": [],
            **pagination_params
        }

        # Фильтрация по жанру
        if genre:
            query_body["query"]["bool"]["must"].append({
                "match": {"genre": genre}
            })

        # Сортировка
        if sort:
            order = "desc" if sort.startswith("-") else "asc"
            field_name = "imdb_rating" \
                if sort[1:] == ("imdb_rating" or sort == "imdb_rating") \
                else sort[1:] if order == "desc" else sort
            query_body["sort"].append({
                field_name: {"order": order}
            })

        try:
            response = await self.elastic.search(index="movies", body=query_body)
        except Exception as e:
            logging.error(f"Failed to fetch films from Elasticsearch: {e}")
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
                logging.error(f"Error validating film data: {e}")
                continue

        return films

    async def search_films(self, query: str,
                           ) -> list[Films]:
        """
        Поиск фильмов по заданному запросу.
        """
        pagination_params = self.pagination.get_pagination_params()
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^5", "description"]
                }
            },
            **pagination_params
        }

        try:
            response = await self.elastic.search(index="movies", body=search_body)
        except Exception as e:
            logging.error(f"Failed to search films in Elasticsearch: {e}")
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
                logging.error(f"Error validating film data: {e}")
                continue

        return films


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
        pagination: Pagination = Depends()
) -> FilmService:
    return FilmService(redis, elastic, pagination)
