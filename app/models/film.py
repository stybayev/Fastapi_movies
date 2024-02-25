from pydantic import Field
from typing import List
from app.models.persons import Actor, Writer
from app.models.base_model import BaseMixin


class Film(BaseMixin):
    """
    Модель фильма
    """
    title: str
    description: str
    imdb_rating: float
    genre: List[str]
    director: List[str] = Field(default_factory=list)
    actors_names: List[str] = Field(default_factory=list)
    writers_names: List[str] = Field(default_factory=list)
    actors: List[Actor] = Field(default_factory=list)
    writers: List[Writer] = Field(default_factory=list)
