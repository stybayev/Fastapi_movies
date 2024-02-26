class Pagination:
    """
    Параметры пагинации
    """
    def __init__(self, page_size: int = 10, page_number: int = 1):
        self.page_size = page_size
        self.page_number = page_number

    def get_pagination_params(self) -> dict:
        return {
            "from": (self.page_number - 1) * self.page_size,
            "size": self.page_size
        }
