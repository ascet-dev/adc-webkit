import dataclasses
import typing as t

from pydantic import BaseModel
from starlette.requests import Request

Q = t.TypeVar('Q', bound=t.Optional[BaseModel])
B = t.TypeVar('B', bound=t.Optional[BaseModel])
H = t.TypeVar('H', bound=t.Optional[BaseModel])


@dataclasses.dataclass
class Ctx(t.Generic[Q, B, H]):
    query: Q
    body: B
    headers: H
    request: Request
    auth_payload: t.Any
