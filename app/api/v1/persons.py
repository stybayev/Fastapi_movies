from fastapi import APIRouter, Depends, Query, Path

from app.models.persons import BasePersonModel
from app.models.film import Films
from app.services.person import get_person_service, PersonsService

router = APIRouter()


@router.get("/{person_id}", response_model=BasePersonModel)
async def get_person_by_id(
        person_id: str = Path(..., description="person's ID"),
        person_service: PersonsService = Depends(get_person_service)
) -> BasePersonModel:
    """
    Получение персоны по id.

    - **person_id**: id персоны
    """
    return await person_service.get_by_id(person_id)


@router.get("/", response_model=list[BasePersonModel])
async def person(
        query: str = Query(description='Search query', default=''),
        page_size: int = Query(10, ge=1, description='Pagination page size'),
        page_number: int = Query(1, ge=1, description='Pagination page number'),
        person_service: PersonsService = Depends(get_person_service)
) -> list[BasePersonModel]:
    """
    Получение списка персон с пагинацией.

    - **query**: поисковый запрос
    - **page_size**: размер страницы
    - **page_number**: номер страницы
    """
    return await person_service.search_person(query, page_size, page_number)


@router.get("/{person_id}/film", response_model=list[Films])
async def get_person_by_id(
        person_id: str = Path(..., description="person's ID"),
        page_size: int = Query(10, ge=1, description='Pagination page size'),
        page_number: int = Query(1, ge=1, description='Pagination page number'),
        person_service: PersonsService = Depends(get_person_service)
) -> list[Films]:
    """
    Получение фильмов по id персоны.

    - **person_id**: id персоны
    - **page_size**: размер страницы
    - **page_number**: номер страницы

    """
    return await person_service.get_films(person_id, page_size, page_number)
