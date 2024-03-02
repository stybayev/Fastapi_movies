from fastapi import Query


async def paginate(
    page_size: int = Query(10, ge=1, le=100, description="Pagination page size"),
    page_number: int = Query(1, ge=1, description="Pagination page number")) -> dict:
    """
    Функция зависимости для извлечения параметров пагинации.
    """
    return {"page_size": page_size, "page_number": page_number}
