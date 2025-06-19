import re
from typing import Optional, Mapping, List

from pydantic import BaseModel

RE_SNAKE_CASE = re.compile(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def camel_case_to_snake_case(value: str) -> str:
    return RE_SNAKE_CASE.sub(r'_\1', value).lower()


class ErrorModel(BaseModel):
    message: str
    errors: Optional[List[str]] = None
    code: Optional[str] = None


class AppError(Exception):
    description: str = 'Application error'
    status_code = 500

    def __init__(
        self,
        message: Optional[str] = None,
        errors: Optional[List[Mapping]] = None,
    ):
        self.message = message or self.description
        self.errors = errors
        self.code = camel_case_to_snake_case(self.__class__.__name__)
        super().__init__(f'AppError {self.code}: message={self.message}, errors={errors}', )

    @property
    def as_dict(self):
        return ErrorModel(
            message=self.message,
            code=self.code,
            errors=[str(err) for err in self.errors] if self.errors else None,
        ).model_dump()


class ServerError(AppError):
    status_code = 500


class IntegrationError(ServerError):
    description = "Integration error"


class ConflictError(ServerError):
    description = "Conflict error"


class NotImplementedServerError(ServerError):
    status_code = 501


class BadRequest(AppError):
    description = 'Bad request'
    status_code = 400


class Unauthorized(BadRequest):
    description = 'Unauthorized'
    status_code = 401


class Forbidden(BadRequest):
    description = 'Forbidden'
    status_code = 403


class NotFound(BadRequest):
    description = 'Not found'
    status_code = 404


class MethodNotAllowed(BadRequest):
    description = 'Method Not Allowed'
    status_code = 405


class RequestTimeout(BadRequest):
    description = 'Request Timeout'
    status_code = 408


class Conflict(BadRequest):
    description = 'Conflict'
    status_code = 409


class Gone(BadRequest):
    description = 'Gone'
    status_code = 410


class PayloadTooLarge(BadRequest):
    description = 'Payload Too Large'
    status_code = 413


class UnprocessableEntity(BadRequest):
    description = 'Unprocessable Entity'
    status_code = 422
