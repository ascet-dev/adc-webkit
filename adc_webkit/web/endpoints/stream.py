from abc import abstractmethod, ABC
from typing import Type, Optional

from pydantic import BaseModel
from starlette.responses import StreamingResponse

from adc_webkit.types import DownloadFile
from .base import Endpoint
from .request_context import Ctx
from adc_webkit.web.body_parsers import ParserFactory, StreamParser


class StreamEndpoint(Endpoint, ABC):
    query: Optional[Type[BaseModel]] = None
    body: Optional[Type[BaseModel]] = None
    headers: Optional[Type[BaseModel]] = None

    @abstractmethod
    async def execute(self, ctx: Ctx[query, body, headers]) -> DownloadFile:
        pass

    async def prepare_response(self, raw_response: DownloadFile):
        response = StreamingResponse(raw_response.file, media_type='application/octet-stream')
        response.headers["Content-Disposition"] = f"attachment; filename={raw_response.filename}"
        return response
