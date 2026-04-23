import html

from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
# SWAGGER_UI_PY_ROOT — internal path of swagger-ui-py; pin the package version in dependencies
from swagger_ui.utils import SWAGGER_UI_PY_ROOT


_SWAGGER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="static/swagger-ui.css" />
    <link rel="stylesheet" type="text/css" href="static/index.css" />
    <link rel="icon" type="image/png" href="static/favicon-32x32.png" sizes="32x32" />
    <link rel="icon" type="image/png" href="static/favicon-16x16.png" sizes="16x16" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="static/swagger-ui-bundle.js" charset="UTF-8"></script>
    <script src="static/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
    <script>
    window.onload = function() {{
        SwaggerUIBundle({{
            url: "swagger.json",
            dom_id: "#swagger-ui",
            deepLinking: true,
            displayRequestDuration: true,
            layout: "StandaloneLayout",
            plugins: [SwaggerUIBundle.plugins.DownloadUrl],
            presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
        }});
    }};
    </script>
</body>
</html>"""


def add_apidoc_routes(web: Starlette, doc: "Doc", apispec: dict) -> None:
    doc_url = doc.url.rstrip('/')
    doc_html = _SWAGGER_HTML.format(title=html.escape(doc.title))

    web.add_route(doc_url + '/swagger.json', route=lambda r: JSONResponse(apispec), methods=["GET"])
    web.mount(doc_url + '/static', StaticFiles(directory=str(SWAGGER_UI_PY_ROOT / 'static')), name='swagger-static')

    async def _doc_page(request):
        return HTMLResponse(doc_html)

    async def _doc_redirect(request):
        # Relative redirect /doc → doc/ — works behind any reverse proxy prefix
        segment = doc_url.rsplit('/', 1)[-1]
        return RedirectResponse(url=segment + '/', status_code=301)

    web.add_route(doc_url + '/', _doc_page, methods=["GET"])
    web.add_route(doc_url, _doc_redirect, methods=["GET"])
