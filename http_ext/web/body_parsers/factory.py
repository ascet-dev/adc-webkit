from typing import Type

from http_ext.types import Base
from .base import Parser


class ParserFactory:
    def __init__(self, parser_cls: Type[Parser], **kwargs):
        self.parser_cls = parser_cls
        self.options = kwargs

    def create_parser(self, schema: Base | None = None, ) -> Parser:
        return self.parser_cls(schema, **self.options)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if getattr(instance, '_body_parser', None) is None:
            instance._body_parser = self.create_parser(instance.body)

        return instance._body_parser
