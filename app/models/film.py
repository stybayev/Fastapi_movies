from pydantic import BaseModel, Field
from typing import List, Optional
import orjson

# Убедитесь, что у вас правильно определены модели Actor и Writer
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
    genre: List[str]
    director: List[str] = Field(default_factory=list)  # Добавлено поле director
    actors_names: List[str] = Field(default_factory=list)
    writers_names: List[str] = Field(default_factory=list)
    actors: List[Actor] = Field(default_factory=list)
    writers: List[Writer] = Field(default_factory=list)
