import json
from typing import Optional

from pydantic import BaseModel, ValidationError, TypeAdapter
from starlette.requests import Request

from http_ext.errors import UnprocessableEntity
from . import Parser


class JsonParser(Parser):
    content_type: str = 'application/json'

    async def load(self, request: Request) -> Optional[BaseModel]:
        if not self.schema:
            return None
        try:
            raw = await request.json()
        except Exception:
            raise UnprocessableEntity('Invalid JSON body')

        if raw is None:
            raise UnprocessableEntity('Empty request body')

        try:
            return TypeAdapter(self.schema).validate_python(raw)
        except ValidationError as exc:
            raise UnprocessableEntity(
                message='Request parameters validation error',
                errors=exc.errors(),
            )
