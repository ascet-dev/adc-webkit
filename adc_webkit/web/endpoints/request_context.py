import dataclasses
import typing as t

from pydantic import BaseModel
from starlette.requests import Request
extended_base_model = t.Union[BaseModel, None, list[BaseModel], dict[str, BaseModel]]

Q = t.TypeVar('Q', bound=extended_base_model)
B = t.TypeVar('B', bound=extended_base_model)
H = t.TypeVar('H', bound=extended_base_model)


@dataclasses.dataclass
class Ctx(t.Generic[Q, B, H]):
    query: Q
    body: B
    headers: H
    request: Request
    auth_payload: t.Any
