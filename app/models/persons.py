from pydantic import Field
from typing import List
from base_model import orjson_dumps, BaseMixin
import orjson


class BasePersonModel(BaseMixin):
    """
    Базовая модель персоны
    """
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
