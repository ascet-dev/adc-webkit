from abc import ABC
from functools import cached_property
from typing import Mapping, Type

from adc_webkit.errors import NotFound
from adc_webkit.types import Base, Paginated, Count, BaseSearch
from adc_webkit.web.auth import HTTPAuth
from adc_webkit.web.openapi import Doc
from adc_aiopg import RowNotFoundError, PGDataAccessObject #todo: refactor adc-aiopg using
from .json import JsonEndpoint
from .request_context import Ctx
from .response import Response


class Endpoint(JsonEndpoint, ABC):
    dao: PGDataAccessObject


class CRUD:
    model: Type[Base]
    tag: str
    query: Type[BaseSearch]
    auth: HTTPAuth | None = None

    @staticmethod
    async def _create(self: Endpoint, ctx: Ctx):
        return await self.dao.create(**ctx.body.model_dump(exclude_unset=True))

    @staticmethod
    async def _update(self: Endpoint, ctx: Ctx):
        return await self.dao.update_by_id(ctx.query.id, **ctx.body.model_dump(exclude_unset=True))

    @staticmethod
    async def _delete(self: Endpoint, ctx: Ctx):
        return await self.dao.archive_by_id(ctx.query.id)

    @staticmethod
    async def _get_by_id(self: Endpoint, ctx: Ctx):
        try:
            return await self.dao.get_by_id(ctx.query.id)
        except RowNotFoundError:
            raise NotFound('ID was not found')

    @staticmethod
    async def _search(self: Endpoint, ctx: Ctx):
        return await self.dao.paginated_search(**ctx.query.model_dump(exclude_unset=True))

    @staticmethod
    async def _count(self: Endpoint, ctx: Ctx):
        total = await self.dao.count(**ctx.query.model_dump(exclude_unset=True))
        return {'total': total}

    @classmethod
    def base_attributes(cls) -> Mapping:
        return {
            'doc': Doc(tags=[cls.tag]),
            'auth': cls.auth,
            'dao': cached_property(lambda endpoint: PGDataAccessObject(  # todo: remove hardcode
                db_pool=endpoint.web.state.app.pg.obj,
                model=cls.model,
            )),
        }

    @classmethod
    def create_endpoint(cls):
        return type(
            f'Create{cls.model.__name__}',
            (Endpoint,),
            {
                **cls.base_attributes(),
                'body': cls.model.exclude('id', 'created', 'updated', 'archived', 'updated_by'),
                'response': Response(cls.model),
                'execute': cls._create
            }
        )

    @classmethod
    def update_endpoint(cls):
        return type(
            f'Update{cls.model.__name__}',
            (Endpoint,),
            {
                **cls.base_attributes(),
                'query': cls.model.only('id'),
                'body': cls.model.exclude('id', 'created', 'updated', 'archived', 'updated_by').partial(),
                'response': Response(cls.model),
                'execute': cls._update
            }
        )

    @classmethod
    def delete_endpoint(cls):
        return type(
            f'Delete{cls.model.__name__}',
            (Endpoint,),
            {
                **cls.base_attributes(),
                'query': cls.model.only('id'),
                'response': Response(cls.model),
                'execute': cls._delete
            }
        )

    @classmethod
    def get_by_id_endpoint(cls):
        return type(
            f'Get{cls.model.__name__}',
            (Endpoint,),
            {
                **cls.base_attributes(),
                'query': cls.model.only('id'),
                'response': Response(cls.model),
                'execute': cls._get_by_id
            }
        )

    @classmethod
    def search_endpoint(cls):
        return type(
            f'Search{cls.model.__name__}',
            (Endpoint,),
            {
                **cls.base_attributes(),
                'query': cls.query,
                'response': Response(Paginated[cls.model]),
                'execute': cls._search
            }
        )

    @classmethod
    def count_endpoint(cls):
        return type(
            f'Count{cls.model.__name__}',
            (Endpoint,),
            {
                **cls.base_attributes(),
                'query': cls.query.exclude('limit', 'offset'),
                'response': Response(Count),
                'execute': cls._count
            }
        )
