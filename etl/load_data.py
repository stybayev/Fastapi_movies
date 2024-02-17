import datetime
import logging
import os
import time

import psycopg2
import redis
import requests
from adapters.elasticsearch_loader import ElasticsearchLoader
from adapters.postgres_extractor import PostgresExtractor
from adapters.redis_state import RedisStorage, State
from backoff import backoff
from config import DBParams, ElasticParams, RedisParams
from connection import postgres_connection
from data_transform import DataTransform
from psycopg2.extensions import connection as _connection

# Максимальный размер выгружаемой пачки
FETCH_LIMIT = 100


def load_filmworks(
    state: State,
    postgres_extractor: PostgresExtractor,
    data_transform: DataTransform,
    elasticsearch_loader: ElasticsearchLoader,
):
    """Процесс загрузки данных для фильмов."""
    last_filmwork = state.get_state("last_filmwork")
    last_filmwork_modified = last_filmwork["modified"] if last_filmwork else None

    for batch in postgres_extractor.get_filmworks(
        last_modified=last_filmwork_modified,
        fetch_limit=FETCH_LIMIT,
    ):
        prepared_batch = data_transform.from_pg_to_elastic(rows=batch)
        elasticsearch_loader.save_batch(batch=prepared_batch)

    state.set_state(
        key="last_filmwork",
        value={"modified": datetime.datetime.utcnow().isoformat()},
    )


def load_related_data(
    state: State,
    postgres_extractor: PostgresExtractor,
    data_transform: DataTransform,
    elasticsearch_loader: ElasticsearchLoader,
    state_name: str,
):
    """Процесс загрузки данных для связанных данных."""
    get_changed = {
        "last_person": postgres_extractor.get_changed_filmworks_by_persons,
        "last_genre": postgres_extractor.get_changed_filmworks_by_genres,
    }

    last_state = state.get_state(state_name)
    last_state_modified = last_state["modified"] if last_state else None

    for filmwork_ids in get_changed[state_name](
        last_modified=last_state_modified,
        fetch_limit=FETCH_LIMIT,
    ):
        filmwork_ids_list = [filmwork["film_work_id"] for filmwork in filmwork_ids]
        for batch in postgres_extractor.get_filmworks_by_ids(
            ids=filmwork_ids_list,
            fetch_limit=FETCH_LIMIT,
        ):
            prepared_batch = data_transform.from_pg_to_elastic(rows=batch)
            elasticsearch_loader.save_batch(batch=prepared_batch)

    state.set_state(
        key=state_name,
        value={"modified": datetime.datetime.utcnow().isoformat()},
    )


def load_from_postgres_to_elasticsearch(
    pg_conn: _connection,
    session: requests.Session,
    redis_conn: redis.Redis,
):
    """Основной процесс загрузки данных из Postgres в Elasticsearch."""
    postgres_extractor = PostgresExtractor(connection=pg_conn)
    elasticsearch_loader = ElasticsearchLoader(params=ElasticParams(), session=session)
    redis_storage = RedisStorage(redis_adapter=redis_conn)
    state = State(storage=redis_storage)
    data_transform = DataTransform()

    params = {
        "state": state,
        "postgres_extractor": postgres_extractor,
        "data_transform": data_transform,
        "elasticsearch_loader": elasticsearch_loader,
    }

    load_filmworks(**params)
    load_related_data(**params, state_name="last_person")
    load_related_data(**params, state_name="last_genre")


@backoff(
    exceptions=(
        redis.exceptions.ConnectionError,
        requests.exceptions.ConnectionError,
        psycopg2.OperationalError,
    ),
    border_sleep_time=10000,
)
def start():
    """Функция инициализации коннектов ко всей необходимой инфраструктуре и
    их передачи в главный процесс загрузки.
    """
    dbparams = DBParams()
    redis_params = RedisParams()
    with (
        postgres_connection(params=dbparams) as pg_conn,
        requests.Session() as session,
        redis.Redis(
            **redis_params.dict(),
            decode_responses=True,
        ) as redis_conn,
    ):
        load_from_postgres_to_elasticsearch(
            pg_conn=pg_conn,
            session=session,
            redis_conn=redis_conn,
        )


class ESIndexNotFoundException(Exception):
    pass


def check_index_exists(index_name: str):
    elastic_params = ElasticParams()

    response = requests.get(
        url=f"http://{elastic_params.url()}/{elastic_params.index_name}",
    )
    if response.status_code == 404:
        os.system(
            f"bash scripts/{index_name}.sh host={elastic_params.host} port={elastic_params.port}",
        )
        raise ESIndexNotFoundException


def main():
    """Главная функция для запуска всего ETL процесса."""
    while True:
        try:
            check_index_exists(index_name="movies")
            start()
        except ESIndexNotFoundException:
            logging.error("ES: No index")
        except requests.exceptions.ConnectionError:
            logging.error("ES: No connection")
        finally:
            sleep_timeout = 5
            logging.info(f"Next etl run in {sleep_timeout} seconds")
            time.sleep(sleep_timeout)


if __name__ == "__main__":
    main()
