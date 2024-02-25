from pydantic import BaseModel, Field
from typing import List
import orjson

from app.models.persons import Actor, Writer
from app.models.utils import orjson_dumps


class BaseFilmModel(BaseModel):
    """
    Базовая модель фильма
    """
    id: str = Field(alias="_id")

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Film(BaseFilmModel):
    """
    Модель фильма
    """
    title: str
    description: str
    imdb_rating: float
    genres: List[str]
    actors: List[str]
    writers: List[str]
    directors: List[str]
    actors_names: List[str] = Field(default_factory=list)
    writers_names: List[str] = Field(default_factory=list)
    actors: List[Actor] = Field(default_factory=list)
    writers: List[Writer] = Field(default_factory=list)

