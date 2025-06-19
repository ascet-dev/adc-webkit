from typing import AsyncGenerator

from starlette.requests import Request

from . import Parser


class StreamParser(Parser):
    content_type: str = 'multipart/form-data'

    @staticmethod
    async def get_generator(request: Request) -> AsyncGenerator[bytes, None]:
        async for chunk in request.stream():
            yield chunk

    async def load(self, request: Request) -> AsyncGenerator[bytes, None]:
        return self.get_generator(request)
