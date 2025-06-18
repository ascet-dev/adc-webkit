import typing as t
from typing import List

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    total: int
    limit: t.Optional[int] = Field(default=0)
    offset: t.Optional[int] = Field(default=0)


class Paginated[T](BaseModel):
    items: List[T]
    pagination: Pagination
