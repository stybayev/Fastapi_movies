from fastapi import APIRouter, Depends
from typing import List

from app.db.elastic import get_elastic, AsyncElasticsearch
from app.models.genre import Genre
from app.utils.paginator import paginate

router = APIRouter()


@router.get("/{genre_id}", response_model=Genre)
async def get_genre_by_id(genre_id: str, es: AsyncElasticsearch = Depends(get_elastic)) -> Genre:
    response = await es.get(index="genres", id=genre_id)
    return Genre(**response['_source'])

@router.get("/", response_model=List[Genre])
async def genre(es: AsyncElasticsearch = Depends(get_elastic), page_params: dict = Depends(paginate)) -> List[Genre]:
    response = await es.search(index="genres", **page_params)
    return [Genre(**item['_source']) for item in response['hits']['hits']]
