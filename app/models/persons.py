from pydantic import Field
from typing import List
import orjson

from app.models.base_model import BaseMixin, orjson_dumps


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
