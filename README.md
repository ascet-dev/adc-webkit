# ADC WebKit

A comprehensive toolkit for building modern web applications with Python. ADC WebKit provides a robust foundation for creating scalable web services with built-in HTTP extensions, authentication, body parsing, and OpenAPI support.

## Features

- **HTTP Extensions**: Enhanced HTTP functionality with custom error handling
- **Web Framework**: Complete web application framework with routing and middleware support
- **Authentication**: Built-in JWT and base authentication systems
- **Body Parsers**: Support for JSON, form data, and streaming request bodies
- **OpenAPI Integration**: Automatic API documentation generation
- **Type Safety**: Full type hints and Pydantic model integration
- **CRUD Operations**: Pre-built CRUD endpoint patterns
- **Response Handling**: Flexible response formatting and streaming

## Installation

```bash
pip install adc-webkit
```

Or install from source:

```bash
git clone https://github.com/ascet-dev/adc-webkit.git
cd adc-webkit
pip install -e .
```

## Quick Start

```python
from adc_webkit.web import WebApplication
from adc_webkit.web.endpoints import JSONEndpoint
from adc_webkit.web.auth import JWTAuth

# Create application
app = WebApplication()

# Define endpoint
class HelloEndpoint(JSONEndpoint):
    async def get(self):
        return {"message": "Hello, World!"}

# Add endpoint to app
app.add_endpoint("/hello", HelloEndpoint)

# Run application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

## Project Structure

```
adc_webkit/
├── __init__.py
├── errors.py              # Custom HTTP error handling
├── types/                 # Type definitions and models
│   ├── __init__.py
│   ├── base_model.py      # Base Pydantic models
│   ├── base_search.py     # Search functionality types
│   ├── count.py          # Count response types
│   ├── file.py           # File handling types
│   ├── http.py           # HTTP-specific types
│   └── pagination.py     # Pagination types
└── web/                   # Web framework components
    ├── __init__.py
    ├── web.py            # Main web application
    ├── auth/             # Authentication modules
    │   ├── __init__.py
    │   ├── base.py       # Base authentication
    │   └── jwt.py        # JWT authentication
    ├── body_parsers/     # Request body parsers
    │   ├── __init__.py
    │   ├── base.py       # Base parser interface
    │   ├── factory.py    # Parser factory
    │   ├── form_data.py  # Form data parser
    │   ├── json.py       # JSON parser
    │   └── stream.py     # Streaming parser
    ├── endpoints/        # Endpoint implementations
    │   ├── __init__.py
    │   ├── base.py       # Base endpoint class
    │   ├── crud.py       # CRUD operations
    │   ├── json.py       # JSON endpoints
    │   ├── request_context.py  # Request context
    │   ├── response.py   # Response handling
    │   └── stream.py     # Streaming endpoints
    └── openapi/          # OpenAPI documentation
        ├── __init__.py
        ├── auth.py       # Auth schema generation
        ├── endpoint.py   # Endpoint schema
        └── schema.py     # Schema utilities
```

## Core Components

### HTTP Extensions (`adc_webkit`)

The main package providing enhanced HTTP functionality:

- Custom error handling with detailed error responses
- Type-safe request/response models
- Pagination support
- File upload/download handling

### Web Framework (`adc_webkit.web`)

A complete web application framework built on top of aiohttp:

- **WebApplication**: Main application class with routing and middleware
- **Endpoints**: Pre-built endpoint patterns for common use cases
- **Authentication**: JWT and base authentication systems
- **Body Parsers**: Flexible request body parsing
- **OpenAPI**: Automatic API documentation generation

### Type System (`adc_webkit.types`)

Comprehensive type definitions using Pydantic:

- Base models for consistent data structures
- Search and pagination types
- HTTP-specific type definitions
- File handling types

## Usage Examples

### CRUD Operations

```python
from adc_webkit.web.endpoints import CRUDEndpoint

class ProductEndpoint(CRUDEndpoint):
    async def list(self):
        return {"products": []}
    
    async def create(self):
        data = await self.get_json()
        return {"created": data}
    
    async def retrieve(self, id: str):
        return {"product": {"id": id}}
    
    async def update(self, id: str):
        data = await self.get_json()
        return {"updated": {"id": id, **data}}
    
    async def delete(self, id: str):
        return {"deleted": id}

app.add_endpoint("/products", ProductEndpoint)
```

### Authentication

```python
from adc_webkit.web.auth import JWTAuth

class ProtectedEndpoint(JSONEndpoint):
    auth_class = JWTAuth
    
    async def get(self):
        user = self.request.user
        return {"message": f"Hello, {user.username}!"}
```

### Custom Body Parser

```python
from adc_webkit.web.body_parsers import BaseBodyParser

class CustomParser(BaseBodyParser):
    async def parse(self, request):
        # Custom parsing logic
        return await request.text()

class CustomEndpoint(JSONEndpoint):
    body_parser_class = CustomParser
```

## Configuration

ADC WebKit supports various configuration options:

```python
app = WebApplication(
    title="My API",
    version="1.0.0",
    description="My awesome API",
    debug=True
)
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/ascet-dev/adc-webkit/issues)
- **Documentation**: ToBe

## Requirements

- Python 3.8+
- python-jose[cryptography]>=3.5.0
- pydantic>=2.11.7
- starlette>=0.47.0
- ujson>=5.10.0 