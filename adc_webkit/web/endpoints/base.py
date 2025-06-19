import re
from abc import abstractmethod, ABC
from functools import cached_property
from logging import getLogger
from typing import Dict, Any, Type, Mapping, Optional

from pydantic import BaseModel, create_model, ValidationError as PydanticValidationError
from starlette.applications import Starlette
from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import JSONResponse

from adc_webkit.errors import BadRequest
from adc_webkit.types import METHOD
from adc_webkit.web import JsonParser, ParserFactory
from adc_webkit.web.auth import HTTPAuth
from adc_webkit.web.openapi import Doc
from .request_context import Ctx
from .response import Response

logger = getLogger(__name__)


class Endpoint(ABC):
    query: Optional[Type[BaseModel]] = None
    body: Optional[Type[BaseModel]] = None
    headers: Optional[Type[BaseModel]] = None

    doc: Doc = Doc()
    auth: HTTPAuth | None = None
    body_parser: ParserFactory = ParserFactory(JsonParser)

    response: Response = Response()

    def __init__(self, path: str, web: Starlette, method: METHOD):
        self.path = path
        self.web = web
        self.method = method
        self.declared_path_params = set(re.findall(r'{(.*?)}', path))

    async def _process_request(self, request: Request):
        try:
            auth_payload = self.auth.execute(request) if self.auth else None
            request_ctx = await self.build_request_ctx(request, auth_payload)
            response = await self.execute(request_ctx)
            return await self.prepare_response(response)
        except tuple(self.response.errors) as e:
            return JSONResponse(e.as_dict, status_code=e.status_code)

    async def process_request(self, request: Request):
        try:
            return await self._process_request(request)
        except Exception as e:
            logger.exception(e)
            return JSONResponse({'message': 'Unknown Server Error'}, status_code=500)

    async def build_request_ctx(self, request, auth_payload) -> Ctx:
        try:
            params = self.get_request_params(request)
            headers = self.get_headers(request.headers)
            body = await self.get_body_params(request)
        except PydanticValidationError as e:
            logger.debug(e)
            raise BadRequest(message=str(e))
        return Ctx(query=params, headers=headers, body=body, request=request, auth_payload=auth_payload)

    def get_headers(self, headers: Dict[str, Any] | Headers) -> 'headers':
        if self.headers:
            return self.headers.model_validate(headers)

    async def get_body_params(self, request: Request) -> 'body':
        return await self.body_parser.load(request)

    def get_request_params(self, request: Request) -> 'query':
        if self.query:
            self.schema_path.model_validate(request.path_params)
            self.schema_query.model_validate(request.query_params)
            return self.query.model_validate({**request.path_params, **request.query_params})

    @cached_property
    def schema_path(self):
        if self.query:
            return create_model(
                f'{self.__class__.__name__}PathParams',
                **{
                    name: (self.query.model_fields[name].annotation, ...)
                    for name in self.declared_path_params
                }
            )

    @cached_property
    def schema_query(self):
        if self.query:
            query_param_names = set(self.query.model_fields.keys()) - self.declared_path_params

            return create_model(
                f'{self.__class__.__name__}QueryParams',
                **{
                    name: (self.query.model_fields[name].annotation, self.query.model_fields[name].default)
                    for name in query_param_names
                }
            )

    @abstractmethod
    async def execute(self, ctx: Ctx[query, body, headers]) -> Mapping | BaseModel:
        pass

    @abstractmethod
    async def prepare_response(self, raw_response):
        pass
