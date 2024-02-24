import orjson

from pydantic import BaseModel
from typing import Callable, Optional, Any


def orjson_dumps(v: Any, *, default: Callable[[Any], Any]) -> str:
    return orjson.dumps(v, default=default).decode()


class Genre(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
