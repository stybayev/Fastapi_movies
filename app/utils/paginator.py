async def paginate(page_size: int = 10, page_number: int = 1) -> dict:
    return {'size': page_size, 'from_': (page_number - 1) * page_size}