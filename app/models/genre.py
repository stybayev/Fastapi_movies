from pydantic import Field
from typing import List
from base_model import orjson_dumps, BaseMixin
import orjson


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
