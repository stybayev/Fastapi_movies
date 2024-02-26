from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from app.services.film import FilmService, get_film_service

router = APIRouter()

from pydantic import BaseModel
from typing import List, Optional


class BaseFilmModelResponse(BaseModel):
    """
    Базовая модель фильма для ответа API
    """
    uuid: str
    title: str
    imdb_rating: float


class BasePersonModelResponse(BaseModel):
    """
    Базовая модель персоны для ответа API
    """
    uuid: str
    full_name: str


class GenreResponse(BaseModel):
    """
    Базовая модель для жанров ответа API
    """
    uuid: str
    name: str


class DirectorResponse(BasePersonModelResponse):
    """
    Модель режиссёра для ответа API
    """
    pass


class ActorResponse(BasePersonModelResponse):
    """
    Модель актера для ответа API
    """
    pass


class WriterResponse(BasePersonModelResponse):
    """
    Модель сценариста для ответа API
    """
    pass


class FilmResponse(BaseFilmModelResponse):
    """
    Модель фильма ответа API
    """
    description: Optional[str] = None
    genre: List[GenreResponse]
    directors: List[DirectorResponse]
    actors: List[ActorResponse]
    writers: List[WriterResponse]


class FilmListResponse(BaseFilmModelResponse):
    """
    Модель для списка фильмов ответа API
    """
    pass


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}', response_model=FilmResponse)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service)) -> FilmResponse:
    """
    Получить информацию о фильме
    :param film_id:
    :param film_service:
    :return:
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')

    # Преобразование данных об актёрах, сценаристах, режиссорах
    actors_response = [ActorResponse(uuid=actor.id, full_name=actor.name) for actor in film.actors]
    writers_response = [WriterResponse(uuid=writer.id, full_name=writer.name) for writer in film.writers]
    directors_response = [DirectorResponse(
        uuid=director.uuid,
        full_name=director.full_name) for director in film.director]

    # Создание и возврат объекта ответа, используя преобразованные данные
    return FilmResponse(
        uuid=film.id,
        title=film.title,
        description=film.description,
        imdb_rating=film.imdb_rating,
        genre=film.genre,
        directors=directors_response,
        actors_names=film.actors_names,
        writers_names=film.writers_names,
        actors=actors_response,
        writers=writers_response
    )


@router.get('/', response_model=List[FilmListResponse])
async def list_films(
        sort: Optional[str] = '-imdb_rating',
        genre: Optional[str] = None,
        page_size: int = 50,
        page_number: int = 1,
        film_service: FilmService = Depends(get_film_service)) -> List[FilmListResponse]:
    """
    Получить список фильмов
    :param sort:
    :param genre:
    :param page_size:
    :param page_number:
    :param film_service:
    :return:
    """
    films = await film_service.get_films(
        sort=sort, genre=genre, page_size=page_size, page_number=page_number)
    return [FilmListResponse(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating) for film in films]
