from fastapi import Query
from pydantic import BaseModel


class Pagination(BaseModel):
    skip: int = 0
    limit: int = 10


def pagination_params(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)) -> Pagination:
    return Pagination(skip=skip, limit=limit)
