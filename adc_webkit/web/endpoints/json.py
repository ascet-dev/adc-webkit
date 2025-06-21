from abc import abstractmethod, ABC
from logging import getLogger
from typing import Type, Mapping, Optional

import ujson
from pydantic import BaseModel, TypeAdapter
from pydantic_core import to_jsonable_python
from starlette.responses import JSONResponse

from .base import Endpoint
from .request_context import Ctx

logger = getLogger(__name__)


class JsonEndpoint(Endpoint, ABC):
    query: Optional[Type[BaseModel]] = None
    body: Optional[Type[BaseModel]] = None
    headers: Optional[Type[BaseModel]] = None

    @abstractmethod
    async def execute(self, ctx: Ctx[query, body, headers]) -> Mapping | BaseModel:
        pass

    async def prepare_response(self, raw_response):
        if self.response.main_resp.model is None:
            return JSONResponse(ujson.dumps(raw_response))

        if isinstance(raw_response, BaseModel):
            raw_response = raw_response.model_dump(exclude_unset=True)

        validated = TypeAdapter(self.response.main_resp.model).validate_python(raw_response)
        return JSONResponse(to_jsonable_python(validated))
