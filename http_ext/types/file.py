from dataclasses import dataclass
from typing import Annotated, AsyncGenerator

from pydantic import PlainValidator, WithJsonSchema
from starlette.datastructures import UploadFile as StarletteUploadFile


class FileValidator:
    def __init__(self, size_ge=None, size_le=None, extension_in=None):
        self.size_ge = size_ge
        self.size_le = size_le
        self.extension_in = extension_in

    def __call__(self, file: StarletteUploadFile):
        file_extension = file.filename.split('.')[-1].lower()

        if self.size_ge and file.size < self.size_ge:
            raise ValueError(f'Размер файла должен быть не меньше {self.size_ge} байт')
        if self.size_le and file.size > self.size_le:
            raise ValueError(f'Размер файла должен быть не больше {self.size_le} байт')
        if self.extension_in and file_extension not in self.extension_in:
            raise ValueError(f'Файл должен иметь одно из следующих расширений: {', '.join(self.extension_in)}')

        return file


def UploadFile(size_ge: int = None, size_le: int = None, extension_in: list[str] = None):
    schema = {'type': 'string', 'format': 'binary'}

    if size_ge:
        schema['minSize'] = size_ge
    if size_le:
        schema['maxSize'] = size_le
    if extension_in:
        schema['extensions'] = extension_in

    return Annotated[
        StarletteUploadFile,
        PlainValidator(FileValidator(size_ge=size_ge, size_le=size_le, extension_in=extension_in)),
        WithJsonSchema(schema)
    ]


@dataclass
class DownloadFile:
    file: AsyncGenerator[bytes, None]
    filename: str
