import datetime

from typing import (
    List,
    NoReturn,
    Optional,
)

from ._core import parse_url
from .objects._core import FileObject
from .objects.gcp import GcpFileObject
from .objects.local import LocalFileObject

_handlers = {
    'file': LocalFileObject,
    'gs': GcpFileObject,
}


def _get_proto(path: str) -> str:
    return parse_url(path)[0]


def get_object(path: str) -> FileObject:
    proto = _get_proto(path)

    return _handlers[proto](path)


def put_object(local_file_name: str, target_object: str) -> NoReturn:
    proto = _get_proto(target_object)

    _handlers[proto].upload(local_file_name, target_object)


def creation_time(path: str) -> datetime.datetime:
    proto = _get_proto(path)

    return _handlers[proto](path).creation_time(path)


def delete_object(path: str) -> NoReturn:
    proto = _get_proto(path)

    _handlers[proto].delete(path)


def list_objects(path: str, pattern: Optional[str] = None) -> List[str]:
    proto = _get_proto(path)

    return _handlers[proto].objects_list(path, pattern=pattern)


def copy_object(source: str, destination: str) -> NoReturn:
    source_proto, _, _ = parse_url(source)
    destination_proto, _, _ = parse_url(destination)

    if source_proto != destination_proto:
        with _handlers[source_proto](source) as file_name:
            _handlers[destination_proto].upload(file_name, destination)
    else:
        _handlers[source_proto].copy(source, destination)
