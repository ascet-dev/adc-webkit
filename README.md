# adc-webkit

Web-фреймворк на базе Starlette для построения async HTTP API. Предоставляет класс-based эндпоинты, JWT-аутентификацию, парсинг тела запроса (JSON, form-data, streaming), типизированный request context через Pydantic и автоматическую генерацию OpenAPI/Swagger.

## Установка

```bash
pip install git+https://github.com/ascet-dev/adc-webkit.git@main
```

## Быстрый старт

```python
import asyncio
from pydantic import BaseModel
from adc_webkit.web import Web, Route
from adc_webkit.web.endpoints import JsonEndpoint, Ctx, Response

class HelloResponse(BaseModel):
    message: str

class HelloEndpoint(JsonEndpoint):
    response = Response(model=HelloResponse)

    async def execute(self, ctx: Ctx) -> dict:
        return {"message": "Hello, World!"}

class API(Web):
    routes = [
        Route(method="GET", path="/hello", view=HelloEndpoint),
    ]

api = API.create()
asyncio.run(api.start("0.0.0.0", 8000))
# Swagger UI: http://localhost:8000/doc
```

## API

### Web

Основной класс приложения. Оборачивает Starlette.

```python
from adc_webkit.web import Web, Route, Doc

class API(Web):
    routes = [
        Route(method="GET", path="/users/{user_id}", view=GetUserEndpoint),
        Route(method="POST", path="/users", view=CreateUserEndpoint),
    ]
    doc = Doc(
        title="My API",
        version="2.0.0",
        description="User management API",
    )

api = API.create()

# Привязка внешних компонентов к lifecycle приложения
api.bind_component("db", db_pool, start_method="start", stop_method="stop")

# Запуск
await api.start("0.0.0.0", 8000, logs_config={})
```

Swagger UI доступен по адресу `/doc`, OpenAPI JSON -- `/doc/swagger.json`.

### Route

```python
from adc_webkit.web import Route

Route(method="GET", path="/users/{user_id}", view=GetUserEndpoint)
```

`method` -- один из: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `OPTIONS`, `HEAD`, `TRACE`.

### Эндпоинты

#### JsonEndpoint

Для эндпоинтов, возвращающих JSON:

```python
from pydantic import BaseModel
from adc_webkit.web.endpoints import JsonEndpoint, Ctx, Response
from adc_webkit.web.openapi import Doc
from adc_webkit.errors import NotFound

class UserQuery(BaseModel):
    user_id: int                  # path-параметр

class UserOut(BaseModel):
    id: int
    name: str

class GetUserEndpoint(JsonEndpoint):
    query = UserQuery             # модель для path + query параметров
    response = Response(model=UserOut, errors=[NotFound])
    doc = Doc(tags=["users"], summary="Get user by ID")

    async def execute(self, ctx: Ctx) -> dict:
        user = await get_user(ctx.query.user_id)
        if not user:
            raise NotFound("User not found")
        return user
```

#### StreamEndpoint

Для потоковой отдачи файлов:

```python
from adc_webkit.web.endpoints import StreamEndpoint, Ctx
from adc_webkit.types import DownloadFile

class DownloadReportEndpoint(StreamEndpoint):
    async def execute(self, ctx: Ctx) -> DownloadFile:
        async def generate():
            yield b"header\n"
            for row in data:
                yield row.encode()

        return DownloadFile(file=generate(), filename="report.csv")
```

Возвращает `StreamingResponse` с `Content-Disposition: attachment`.

### Request Context (Ctx)

Типизированный контекст запроса, передаваемый в `execute`:

```python
@dataclass
class Ctx(Generic[Q, B, H]):
    query: Q          # path + query параметры (Pydantic model)
    body: B           # тело запроса (Pydantic model)
    headers: H        # заголовки (Pydantic model)
    request: Request  # оригинальный Starlette Request
    auth_payload: Any # результат аутентификации
```

Модели для query, body, headers указываются как атрибуты класса эндпоинта:

```python
class CreateUserBody(BaseModel):
    name: str
    email: str

class CreateUserEndpoint(JsonEndpoint):
    query = None                  # нет path/query параметров
    body = CreateUserBody         # парсинг тела запроса
    headers = None                # нет валидации заголовков

    async def execute(self, ctx: Ctx) -> dict:
        return await create_user(ctx.body.name, ctx.body.email)
```

### Response

Описание ответа эндпоинта (для OpenAPI и валидации):

```python
from adc_webkit.web.endpoints import Response

Response(
    model=UserOut,          # Pydantic модель ответа
    status_code=200,        # HTTP статус
    description="success",  # описание для OpenAPI
    errors=[NotFound, BadRequest],  # ошибки для OpenAPI
)
```

### Аутентификация

#### JWT

```python
from adc_webkit.web.auth import JWT

jwt_auth = JWT(
    public_key="-----BEGIN PUBLIC KEY-----\n...",
    algorithms=["RS256"],
    audience="my-api",
)

class ProtectedEndpoint(JsonEndpoint):
    auth = jwt_auth

    async def execute(self, ctx: Ctx) -> dict:
        user_id = ctx.auth_payload["sub"]
        return {"user_id": user_id}
```

JWT читает заголовок `Authorization: Bearer <token>`, декодирует через `python-jose`.

Для динамического получения публичного ключа (JWKS) -- наследуйте `JWT` и переопределите `get_public_key(request)`.

#### Кастомная аутентификация

```python
from adc_webkit.web.auth import HTTPAuth

class APIKeyAuth(HTTPAuth):
    header_name = "X-API-Key"

    async def get_auth_payload(self, request) -> dict:
        key = request.headers.get(self.header_name)
        if key != "expected-key":
            raise Unauthorized("Invalid API key")
        return {"api_key": key}
```

### Body Parsers

По умолчанию используется `JsonParser`. Можно переключить:

```python
from adc_webkit.web.body_parsers import FormDataParser, StreamParser, ParserFactory

# Form data (multipart/form-data)
class UploadEndpoint(JsonEndpoint):
    body = UploadSchema
    body_parser = ParserFactory(FormDataParser, max_files=10)

# Raw stream
class StreamUploadEndpoint(JsonEndpoint):
    body_parser = ParserFactory(StreamParser)
```

### Типы файлов

```python
from adc_webkit.types import UploadFile, DownloadFile

class UploadSchema(BaseModel):
    file: UploadFile(size_le=10_000_000, extension_in=[".jpg", ".png"])
    description: str
```

`UploadFile()` -- фабрика, возвращающая Pydantic Annotated-тип с валидацией размера и расширения.

### Ошибки

Все ошибки наследуют `AppError` и автоматически конвертируются в JSON-ответ:

```python
from adc_webkit.errors import (
    BadRequest,         # 400
    Unauthorized,       # 401
    Forbidden,          # 403
    NotFound,           # 404
    MethodNotAllowed,   # 405
    RequestTimeout,     # 408
    Conflict,           # 409
    Gone,               # 410
    PayloadTooLarge,    # 413
    UnprocessableEntity,# 422
    ServerError,        # 500
    IntegrationError,   # 500
)

raise NotFound("User not found")
raise BadRequest("Invalid email", errors=["email must contain @"])
```

Формат ответа:
```json
{"message": "User not found", "errors": [], "code": 404}
```

## Примеры

### CRUD API

```python
from pydantic import BaseModel
from adc_webkit.web import Web, Route
from adc_webkit.web.endpoints import JsonEndpoint, Ctx, Response
from adc_webkit.web.openapi import Doc
from adc_webkit.web.auth import JWT
from adc_webkit.errors import NotFound

jwt = JWT(public_key="...", algorithms=["RS256"])

class ItemId(BaseModel):
    item_id: int

class ItemBody(BaseModel):
    name: str
    price: float

class ItemOut(BaseModel):
    id: int
    name: str
    price: float

class GetItem(JsonEndpoint):
    query = ItemId
    auth = jwt
    response = Response(model=ItemOut, errors=[NotFound])
    doc = Doc(tags=["items"], summary="Get item")

    async def execute(self, ctx: Ctx) -> dict:
        item = await db.items.get_by_id(ctx.query.item_id)
        if not item:
            raise NotFound("Item not found")
        return item

class CreateItem(JsonEndpoint):
    body = ItemBody
    auth = jwt
    response = Response(model=ItemOut, status_code=201)
    doc = Doc(tags=["items"], summary="Create item")

    async def execute(self, ctx: Ctx) -> dict:
        return await db.items.create(**ctx.body.model_dump())

class API(Web):
    routes = [
        Route(method="GET", path="/items/{item_id}", view=GetItem),
        Route(method="POST", path="/items", view=CreateItem),
    ]
    doc = Web.doc.__class__(title="Items API", version="1.0.0")

api = API.create()
```

## Требования

- Python >= 3.8
- starlette >= 0.47.0
- uvicorn >= 0.27.0
- pydantic >= 2.11.7
- python-jose[cryptography] >= 3.5.0
- ujson >= 5.10.0
- swagger-ui-py

## Лицензия

MIT
