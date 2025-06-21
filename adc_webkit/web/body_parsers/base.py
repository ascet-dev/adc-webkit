from abc import abstractmethod, ABC

from pydantic import BaseModel
from starlette.requests import Request


class Parser(ABC):
    content_type: str

    @abstractmethod
    async def load(self, request: Request):
        pass

    def __init__(self, schema: type[BaseModel], **kwargs):
        self.schema = schema
