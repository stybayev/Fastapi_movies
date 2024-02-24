from fastapi import APIRouter, Depends
from typing import Annotated

from db.elastic import get_elastic, AsyncElasticsearch
from models.genre import Genre

router = APIRouter()


@router.get("/{genre_id}", response_model=Genre)
async def genre(genre_id: str, es: AsyncElasticsearch = Depends(get_elastic)) -> Genre:
    response = await es.get(index="genres", id=genre_id)
    return Genre(**response['_source'])