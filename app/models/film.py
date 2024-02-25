from pydantic import Field, BaseModel as BaseModelFromPydantic
from typing import List, Optional
from app.models.base_model import BaseMixin


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


class Film(BaseMixin):
    """
    Модель фильма
    """
    title: str
    description: Optional[str] = None
    imdb_rating: float
    genre: List[Genre] = Field(default_factory=list)
    director: List[Director] = Field(default_factory=list)
    actors_names: List[str] = Field(default_factory=list)
    writers_names: List[str] = Field(default_factory=list)
    actors: List[Actor] = Field(default_factory=list)
    writers: List[Writer] = Field(default_factory=list)
