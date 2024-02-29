from fastapi import APIRouter, Depends
from typing import List

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

@router.get("/", response_model=List[BasePersonModel])
async def person(
    query: str = '',
    person_service: PersonsService = Depends(get_person_service)
) -> List[BasePersonModel]:
    return await person_service.search_person(query)

@router.get("/{person_id}/film", response_model=List[Films])
async def get_person_by_id(
                    person_id: str,
                    person_service: PersonsService = Depends(get_person_service)
                ) -> List[Films]:
    return await person_service.get_films(person_id)

