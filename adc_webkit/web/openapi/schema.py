import urllib.parse
from typing import TYPE_CHECKING, Type

from pydantic import BaseModel, TypeAdapter

from .auth import build_security_definition

if TYPE_CHECKING:
    from adc_webkit.web import Endpoint


def get_schema_name(sc):  # todo: move it to usage
    if sc.get('title'):
        return sc['title'].replace("[", "_").replace("]", "_")
    if sc.get('$ref'):
        return sc['$ref'].split('/')[-1]
    if sc.get('anyOf'):
        return '_or_'.join(get_schema_name(item) for item in sc['anyOf'])
    if sc.get('type'):
        return sc['type'].capitalize() + get_schema_name(sc.get('items', {}))
    return ''


def build_openapi_doc(title: str, description: str, version: str, endpoints: list['Endpoint']) -> dict:
    paths_dict = {}
    components_schemas = {}
    security_schemes = {}

    def add_schema(model: Type[BaseModel]):
        if not model:
            return
        model = TypeAdapter(model)
        schema_dict = model.json_schema(ref_template='#/components/schemas/{model}')
        defs = schema_dict.pop('$defs', {})
        for sc in [*defs.values(), schema_dict]:
            schema_name = get_schema_name(sc)
            components_schemas[schema_name] = sc
        return schema_name

    def get_ref(model: Type[BaseModel]):
        schema_name = add_schema(model)
        encoded_ref = urllib.parse.quote(f"#/components/schemas/{schema_name}", safe='#/')
        return encoded_ref

    def add_security_scheme(auth):
        s_name, scheme = build_security_definition(auth)
        security_schemes[s_name] = scheme
        return s_name

    for endpoint in endpoints:
        if endpoint.path not in paths_dict:
            paths_dict[endpoint.path] = {}

        operation = {
            "summary": endpoint.doc.summary or '',
            "tags": endpoint.doc.tags,
            "description": endpoint.doc.description or '',
            "operationId": endpoint.doc.operation_id,
            "parameters": [],
            "responses": {
                str(response.status_code): {
                    "description": response.description,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": get_ref(response.model)
                            }
                        }
                    }
                } for response in endpoint.response.responses
            }
        }
        if endpoint.auth:
            security_scheme_name = add_security_scheme(endpoint.auth)
            operation['security'] = [{security_scheme_name: []}]

        if endpoint.method.lower() != "get" and endpoint.body:
            operation["requestBody"] = {
                "content": {
                    endpoint.body_parser.content_type: {
                        "schema": {
                            "$ref": get_ref(endpoint.body)
                        }
                    }
                }
            }

        if endpoint.schema_path:
            path_params = endpoint.schema_path.schema().get("properties", {})
            for name, schema in path_params.items():
                operation["parameters"].append({
                    "in": "path",
                    "name": name,
                    "required": True,
                    "schema": schema
                })
            add_schema(endpoint.schema_path)

        if endpoint.schema_query:
            query_params = endpoint.schema_query.schema().get("properties", {})
            for name, schema in query_params.items():
                operation["parameters"].append({
                    "in": "query",
                    "name": name,
                    "required": False,
                    "schema": schema
                })
            add_schema(endpoint.schema_query)

        paths_dict[endpoint.path][endpoint.method.lower()] = operation

    for schema in components_schemas.values():
        if 'properties' in schema:
            for prop_name, prop in schema['properties'].items():
                if isinstance(prop, dict) and '$ref' in prop:
                    ref_schema_name = prop['$ref'].split('/')[-1]
                    prop['$ref'] = f"#/components/schemas/{ref_schema_name}"

    return {
        "openapi": "3.1.0",
        "info": {
            "title": title,
            "description": description,
            "version": version
        },
        "paths": paths_dict,
        "components": {
            "schemas": components_schemas,
            'securitySchemes': security_schemes,
        },
    }
