from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Literal, Mapping, Any, Type

from pydantic import BaseModel
from starlette.requests import Request

from adc_webkit.errors import Unauthorized

T = TypeVar('T', bound=Type[BaseModel])
SCHEME = Literal['bearer', 'basic']


class HTTPAuth(ABC, Generic[T]):
    header_name: str = 'Authorization'
    description: str = 'HTTP'
    scheme: SCHEME = 'Bearer'

    payload_model: T

    def __init__(self, payload_model: T | None = None, **kwargs):
        self.ctx = kwargs
        self.payload_model = payload_model

    @abstractmethod
    def get_auth_payload(self, request) -> Mapping[str, Any]:
        pass

    def execute(self, request: Request) -> T:
        try:
            auth_payload = self.get_auth_payload(request)
            if self.payload_model:
                auth_payload = self.payload_model.model_validate(auth_payload)
            return auth_payload
        except Exception as e:
            raise Unauthorized(str(e))
