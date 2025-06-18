from typing import Type, Optional, Iterable, Any

from pydantic import BaseModel

from http_ext.errors import AppError, ErrorModel, ConflictError


class SResponse(BaseModel):
    model: Type[BaseModel] | Any = None
    description: Optional[str] = None
    status_code: int = 200


class Response:
    def __init__(
        self,
        model: Type[BaseModel] | Any = None,
        status_code: int = 200,
        description: str = 'success',
        errors: Iterable[Type[AppError]] = (),
    ):
        self.errors = set()
        self.main_resp = SResponse(model=model, description=description, status_code=status_code)
        self.responses = [self.main_resp]
        self.register_errors((*errors, AppError))

    def add(self, status_code: int, model: Type[BaseModel], description: Optional[str] = None) -> None:
        if any(r.status_code == status_code for r in self.responses):
            raise ConflictError('Status code is already registered')
        r = SResponse(model=model, description=description, status_code=status_code)
        self.responses.append(r)

    def register_errors(self, errors: Iterable[Type[AppError]]) -> None:
        for error in errors:
            self.errors.add(error)
            self.responses.append(
                SResponse(
                    model=ErrorModel,
                    description=error.description,
                    status_code=error.status_code
                )
            )
