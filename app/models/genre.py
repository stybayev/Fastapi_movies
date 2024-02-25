from pydantic import Field
from typing import List
import orjson

from app.models.base_model import BaseMixin, orjson_dumps


class Genre(BaseMixin):
    """
    Модель жанра
    """
    id: str = Field(alias="_id")
    name: str
    films: List[str]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
