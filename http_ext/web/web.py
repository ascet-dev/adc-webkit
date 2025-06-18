import asyncio
import dataclasses
import signal
from typing import Type, List, Self, Dict, Any

import uvicorn
from pydantic import BaseModel
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from swagger_ui import api_doc

from http_ext.types import METHOD
from . import Endpoint
from .openapi.schema import build_openapi_doc


@dataclasses.dataclass
class Route:
    method: METHOD
    path: str
    view: Type[Endpoint]


class Doc(BaseModel):
    title: str = "API Documentation"
    version: str = "1.0.0"
    description: str = "API Documentation"
    openapi_version: str = "3.0.0"
    url: str = '/doc'


class Web:
    routes: list[Route]
    doc: Doc = Doc()
    cors: Dict[str, Any] = {}
    state: Dict[str, Any]

    def __init__(self, web: Starlette, views: List[Endpoint]):
        self.web = web
        self.state = {}
        self.views = views
        self.apispec = build_openapi_doc(
            title=self.doc.title,
            version=self.doc.version,
            description=self.doc.description,
            endpoints=self.views,
        )
        web.add_route(self.doc.url + '/swagger.json', route=lambda r: JSONResponse(self.apispec), methods=["GET"])
        api_doc(web, config_url='/swagger.json', url_prefix=self.doc.url, title=self.doc.title, editor=True)

    @classmethod
    def create(cls, bindings: Dict[str, Any] = None) -> Self:
        web = Starlette(
            debug=True,
            middleware=[Middleware(CORSMiddleware, **cls.cors)]
        )
        views = []

        for route in cls.routes:
            view = route.view(web=web, path=route.path, method=route.method)
            web.add_route(path=view.path, route=view.process_request, methods=[str(view.method)])
            views.append(view)
        web_app = cls(web, views)
        if not bindings:
            return web_app
        for attr, component in bindings.items():
            web_app.bind_component(attr, component)
        return web_app

    async def start(self, host: str, port: int, logs_config: dict) -> None:
        config = uvicorn.Config(
            self.web,
            host=host,
            port=port,
            log_config=logs_config,
        )
        server = uvicorn.Server(config)

        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)

        await server.serve()
        await stop_event.wait()
        if not server.should_exit:
            await server.shutdown()

    def bind_component(
        self,
        attr: str,
        component: Any,
        start_method: str | None = 'start',
        stop_method: str | None = 'stop',
    ) -> None:
        self.state[attr] = component
        self.web.add_event_handler('startup', getattr(component, start_method))
        self.web.add_event_handler('shutdown', getattr(component, stop_method))
        setattr(self.web.state, attr, component)
