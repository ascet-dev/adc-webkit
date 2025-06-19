import re
from typing import List, Mapping, Any

from jose import jwt
from pydantic import BaseModel
from starlette.requests import Request

from .base import HTTPAuth
from adc_webkit.errors import Unauthorized


class DecodeParams(BaseModel):
    auth_scheme: str = 'Bearer'
    algorithms: List[str] = ['RS256']
    audience: str | None = None
    public_key: str | None = None


class JWT(HTTPAuth):
    description: str = 'JWT'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.decode_parameters = DecodeParams.model_validate(kwargs)

    def get_public_key(self, request: Request) -> str:
        if self.decode_parameters.public_key:
            return self.decode_parameters.public_key
        else:
            raise NotImplemented

    def get_auth_payload(self, request: Request) -> Mapping[str, Any]:
        header = request.headers.get('Authorization')
        if not header:
            raise Unauthorized('Missing authorization token')
        try:
            current_auth_scheme, access_token = header.strip().split()
        except ValueError:
            raise Unauthorized('Invalid authorization header')

        if not re.match(current_auth_scheme, self.decode_parameters.auth_scheme):
            raise Unauthorized('Invalid token scheme')

        try:
            return jwt.decode(
                token=access_token,
                key=self.get_public_key(request=request),
                algorithms=self.decode_parameters.algorithms,
                audience=self.decode_parameters.audience,
            )
        except jwt.JWTError as e:
            raise Unauthorized(f'Invalid Token. {e}')
