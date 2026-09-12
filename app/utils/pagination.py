from pydantic import BaseModel


class ParametresPagination(BaseModel):
    skip: int = 0
    limit: int = 100


def valider_pagination(skip: int = 0, limit: int = 100) -> ParametresPagination:
    skip = max(skip, 0)
    limit = min(max(limit, 1), 200)
    return ParametresPagination(skip=skip, limit=limit)
