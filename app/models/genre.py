import orjson

from pydantic import BaseModel
from typing import Callable, Optional, Any
from app.models.base_model import BaseMixin, orjson_dumps

class Genre(BaseMixin):
    name: str
    description: Optional[str] = None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
