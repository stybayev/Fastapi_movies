from pydantic import BaseModel, Field
from typing import List
from utils import orjson_dumps
import orjson


class BasePersonModel(BaseModel):
    """
    Базовая модель персоны
    """
    id: str = Field(alias="_id")
    full_name: str
    films: List[str]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


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


class Director(BasePersonModel):
    """
    Модель режиссера, связанная с фильмом
    """
    pass
