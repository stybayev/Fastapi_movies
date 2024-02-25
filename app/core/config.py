import os
from logging import config as logging_config

from app.core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Настройки основного приложения
UVICORN_HOST = os.getenv("UVICORN_HOST", "0.0.0.0")
UVICORN_PORT = int(os.getenv("UVICORN_PORT", 8000))

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "0.0.0.0")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "0.0.0.0")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
