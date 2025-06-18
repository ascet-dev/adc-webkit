from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from http_ext.web import Endpoint


class Doc(BaseModel):
    tags: list[str] = None
    summary: str = None
    description: str = None
    operation_id: str = None

    def __get__(self, instance: 'Endpoint', owner):
        if owner is not None and self.operation_id is None:
            self.operation_id = owner.__name__
        return self
