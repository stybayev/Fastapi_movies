from pydantic import BaseModel, Field
from typing import List
from utils import orjson_dumps
import orjson


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
