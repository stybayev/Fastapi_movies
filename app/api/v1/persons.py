from fastapi import APIRouter, Depends, Query

from app.models.persons import BasePersonModel
from app.models.film import Films
from app.services.person import get_person_service, PersonsService

router = APIRouter()


@router.get("/{person_id}", response_model=BasePersonModel)
async def get_person_by_id(
        person_id: str,
        person_service: PersonsService = Depends(get_person_service)
) -> BasePersonModel:
    return await person_service.get_by_id(person_id)


@router.get("/", response_model=list[BasePersonModel])
async def person(
        query: str = '',
        page_size: int = Query(10, ge=1, description='Pagination page size'),
        page_number: int = Query(1, ge=1, description='Pagination page number'),
        person_service: PersonsService = Depends(get_person_service)
) -> list[BasePersonModel]:
    return await person_service.search_person(query, page_size, page_number)


@router.get("/{person_id}/film", response_model=list[Films])
async def get_person_by_id(
        person_id: str,
        page_size: int = Query(10, ge=1, description='Pagination page size'),
        page_number: int = Query(1, ge=1, description='Pagination page number'),
        person_service: PersonsService = Depends(get_person_service)
) -> list[Films]:
    return await person_service.get_films(person_id, page_size, page_number)
