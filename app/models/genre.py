from pydantic import BaseModel, Field
from typing import List
from utils import orjson_dumps
import orjson


class Genre(BaseModel):
    """
    Модель жанра
    """
    id: str = Field(alias="_id")
    name: str
    films: List[str]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
