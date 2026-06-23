import datetime
import os
import re
import tempfile
from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import (
    List,
    NoReturn,
    Optional,
    Tuple,
)

from .._core import parse_url


class FileObject(metaclass=ABCMeta):
    """
    A helper abstract class which allows to access file objects regardless
    where files are located.

    The class is not threadsafe.

    Args:
        path: A path to a file object to be accessed. For local files protocol
            may be missing, but for remote ones it's mandatory, i.e.
            `'gs://client-games-gcs-bucket/path/to/file/object'`.
    """
    def __init__(self, path: str):
        if not hasattr(self, '_proto'):
            raise ValueError('User must define a supported protocol in '
                             '`_proto` class variable')

        self._netloc, self._path = self._parse_path(path)
        self._tmp_dir = None

    @classmethod
    def _parse_path(cls, path: str) -> Tuple[str, str]:
        proto, netloc, path = parse_url(path)

        cls._check_proto(proto=proto)

        return netloc, path

    @classmethod
    def _check_proto(cls, *, path: Optional[str] = None,
                     proto:  Optional[str] = None) -> NoReturn:
        if path is not None:
            assert proto is None
            proto, _, _ = parse_url(path)

        assert proto == cls._proto

    def __enter__(self) -> str:
        """
        A context interface, which allows access to an object. File should be
        downloaded locally in case if it's remote one.

        So, the instance of an exact implementation of FileObject may be used
        as a context:

        >>> with SomeFileObject('gs://client-games-gcs-bucket/path/to/file.name') as file_name:
        >>>     print('Local file name:', file_name)

        Returns:
            A local path to the file.
        """
        self._tmp_dir = tempfile.TemporaryDirectory()

        return self._enter(self._tmp_dir.name)

    @abstractmethod
    def _enter(self, tmp_dir: str) -> str:
        """
        A method to be implemented in a superclass.

        Args:
            tmp_dir: A temporary directory to download remote file to. File
            name should be preserved.

        Returns:
            A path to a local file.
        """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit(exc_type, exc_val, exc_tb)

        self._tmp_dir.cleanup()
        self._tmp_dir = None

    @abstractmethod
    def _exit(self, exc_type, exc_val, exc_tb) -> NoReturn:
        """
        User defined actions on leaving the context of the file object.

        Args:
            exc_type:
            exc_val:
            exc_tb:

        Returns:

        """
        pass

    @classmethod
    def upload(cls, local_file_name: str, target_object: str,
               force: bool = False) -> NoReturn:
        """
        Upload a local file to a remote location.

        Args:
            local_file_name: A path to a local file.
            target_object: Target object name, including protocol (may be
                missing for local files). I.e.
                `'gs://client-games-gcs-bucket/path/to/file'` or `'/path/to/file'` for
                local files).
            force: Overwrite an existing remote object, if any. If remote
                object exists, but `force` is `False`, an exception should be
                risen.
        """
        target_proto, target_netloc, target_path = parse_url(target_object)

        cls._check_proto(proto=target_proto)

        return cls._upload_object(local_file_name, target_netloc, target_path,
                                  force=force)

    @classmethod
    @abstractmethod
    def _upload_object(cls, local_file_name: str, netloc: str, path: str,
                       force: bool = False) -> NoReturn:
        """
        Upload local file to a target location.

        Args:
            local_file_name: A path to a local file.
            netloc: Network location. I.e. `client-games-gcs-bucket` for
                `'gs://client-games-gcs-bucket/path/to/file'` or `''` for `'/path/to/file'`.
            path: A path to file. I.e. `'/path/to/file'` for both
                `'gs://client-games-gcs-bucket/path/to/file'` and `'/path/to/file'`.
            force: Whether existing target may be overwritten.
        """
        pass

    @classmethod
    def creation_time(cls, path: str) -> datetime.datetime:
        """
        Return an object creation time.

        Args:
            path: A path to an object.

        Returns:
            A `datetime.datetime` object with the object creation time.
        """
        cls._check_proto(path=path)

        return cls._creation_time(path)

    @classmethod
    @abstractmethod
    def _creation_time(cls, path: str) -> datetime.datetime:
        pass

    @classmethod
    def delete(cls, path: str) -> NoReturn:
        """
        Delete an object by a given URL path.

        Args:
            path: A path to an object to be deleted.
        """
        cls._check_proto(path=path)
        cls._delete(path)

    @classmethod
    @abstractmethod
    def _delete(cls, path: str) -> NoReturn:
        pass

    @classmethod
    def objects_list(cls, path: str,
                     pattern: Optional[str] = None) -> List[str]:
        """
        Return a list of object by a given path.

        Args:
            path: A path, where objects should be found.
            pattern: A regex pattern which object names should comply.

        Returns:
            A list of objects with a given constraints.
        """
        cls._check_proto(path=path)

        def _filter_object(path: str, pattern: re.Pattern) -> bool:
            object_name = os.path.basename(path)
            return pattern.fullmatch(object_name) is not None

        objects_list = cls._objects_list(path)

        if pattern is not None:
            pattern = re.compile(pattern)

            objects_list = [object_name for object_name in objects_list
                            if _filter_object(object_name, pattern)]

        return objects_list

    @classmethod
    @abstractmethod
    def _objects_list(cls, path: str) -> List[str]:
        """
        List of all the objects by a given path.

        Args:
            path: A path to a file object.

        Returns:
            A list of object file names.
        """
        pass

    @classmethod
    def exists(cls, path: str) -> bool:
        cls._check_proto(path=path)

        return cls._exists(path)

    @classmethod
    @abstractmethod
    def _exists(cls, path: str) -> bool:
        pass

    @classmethod
    def copy(cls, source: str, destination: str,
             force: bool = False) -> NoReturn:
        """
        Both objects should be handled by the same protocol.

        Args:
            source: A path to a source object.
            destination: A path to a destination object.
            force: Overwrite existing destination if any.
        """
        proto_source, _, _ = parse_url(source)
        proto_destination, _, _ = parse_url(destination)

        assert proto_source == cls._proto
        assert proto_destination == cls._proto

        if cls.exists(destination) and not force:
            raise ValueError(f'Cannot copy "{source}" to "{destination}": '
                             'destination exists, but `force` is `False`')

        cls._copy(source, destination)

    @classmethod
    @abstractmethod
    def _copy(cls, source: str, destination: str) -> NoReturn:
        pass
