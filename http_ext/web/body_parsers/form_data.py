from typing import Optional, Dict, Any, get_origin

from pydantic import BaseModel, ValidationError
from starlette.datastructures import FormData
from starlette.requests import Request

from http_ext.errors import UnprocessableEntity
from . import Parser


class FormDataParser(Parser):
    content_type: str = 'multipart/form-data'

    def __init__(
        self,
        schema: Optional[type[BaseModel]] = None,
        max_files: Optional[int] = 100,
        **kwargs
    ):
        super().__init__(schema, **kwargs)
        self.max_files = max_files

    def get_body(self, form: FormData) -> Dict[str, Any]:
        body = {}
        for field_name, field in self.schema.model_fields.items():
            if get_origin(field.annotation) is list:
                body[field_name] = form.getlist(field_name)
            else:
                body[field_name] = form.get(field_name)
        return body

    async def load(self, request: Request) -> Optional[BaseModel]:
        if not self.schema:
            return None
        try:
            form: FormData = await request.form(max_files=self.max_files)
        except Exception as exc:
            raise UnprocessableEntity('Неверные данные формы') from exc

        body = self.get_body(form)
        try:
            return self.schema.model_validate(body)
        except ValidationError as exc:
            raise UnprocessableEntity(
                message='Ошибка валидации параметров запроса',
                errors=exc.errors(),
            )
