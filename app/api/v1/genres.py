from fastapi import APIRouter, Depends, Query

from app.db.elastic import get_elastic, AsyncElasticsearch
from app.models.genre import Genre

router = APIRouter()


@router.get("/{genre_id}", response_model=Genre)
async def get_genre_by_id(genre_id: str,
                          es: AsyncElasticsearch = Depends(get_elastic)) -> Genre:
    response = await es.get(index="genres", id=genre_id)
    return Genre(**response['_source'])


@router.get("/", response_model=list[Genre])
async def genre(es: AsyncElasticsearch = Depends(get_elastic),
                page_size: int = Query(10, ge=1, description='Pagination page size'),
                page_number: int = Query(1, ge=1, description='Pagination page number'),

                ) -> list[Genre]:
    """
    Получение списка жанров с пагинацией.
    """
    offset = (page_number - 1) * page_size

    response = await es.search(
        index="genres",
        body={"from": offset, "size": page_size},
    )
    return [Genre(**item['_source']) for item in response['hits']['hits']]
