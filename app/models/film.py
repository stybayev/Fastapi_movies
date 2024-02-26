from pydantic import Field, BaseModel as BaseModelFromPydantic
from typing import List, Optional
from app.models.base_model import BaseMixin, BaseFilm


class BasePersonModel(BaseMixin):
    """
    Базовая модель персоны
    """
    name: str


class Genre(BaseModelFromPydantic):
    """
    Модель жанра, связанная с фильмом
    """
    uuid: str
    name: str


class Director(BaseModelFromPydantic):
    """
    Модель режисреа, связанная с фильмом
    """
    uuid: str
    full_name: str


class Actor(BasePersonModel):
    """
    Модель актера, связанная с фильмом
    """
    pass


class Writer(BasePersonModel):
    """
    Модель сценариста, связанная с фильмом
    """
    pass


class Film(BaseFilm):
    """
    Модель фильма
    """
    description: Optional[str] = None
    genre: List[Genre] = Field(default_factory=list)
    director: List[Director] = Field(default_factory=list)
    actors_names: List[str] = Field(default_factory=list)
    writers_names: List[str] = Field(default_factory=list)
    actors: List[Actor] = Field(default_factory=list)
    writers: List[Writer] = Field(default_factory=list)


class Films(BaseFilm):
    """
    Модель фильмов
    """
    id: str
    title: str
    imdb_rating: Optional[float] = None
