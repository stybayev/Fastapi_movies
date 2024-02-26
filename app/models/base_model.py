from typing import Optional

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class BaseMixin(BaseModel):
    """
    Базовая модель
    """
    id: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

class BaseFilm(BaseMixin):
    """
    Базовая модель фильма
    """
    title: str
    imdb_rating: Optional[float] = None
