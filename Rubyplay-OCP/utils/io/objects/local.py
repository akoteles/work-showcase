import datetime
import glob
import logging
import os
import shutil
from typing import NoReturn, List

from ._core import FileObject

_log = logging.getLogger('LocalFileObject')


class LocalFileObject(FileObject):
    _proto = 'file'

    def __init__(self, path: str):
        super(LocalFileObject, self).__init__(path)
        assert self._proto == 'file'
        assert self._netloc == ''

    def _enter(self, tmp_dir: str) -> str:
        _log.debug('Using local file: "%s"', self._path)
        return self._path

    def _exit(self, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    def _upload_object(cls, local_file_name: str, netloc: str, path: str,
                       force: bool = False) -> NoReturn:
        _log.debug('Copying local file: "%s" -> "%s"', local_file_name,
                       path)

        target_dir = os.path.dirname(path)

        if not os.path.exists(target_dir):
            _log.warning('Target directory "%s" does not exist, making it',
                         target_dir)
            os.makedirs(target_dir, 0o700)

        if os.path.exists(path):
            if not force:
                msg = (f'Target object "{path}" exists. Pass `force=True` to '
                       'overwrite it')
                _log.error(msg)
                raise RuntimeError(msg)
            else:
                _log.warning('Overwriting existing file object "%s"', path)

        shutil.copy2(local_file_name, path)

    @classmethod
    def _creation_time(cls, path: str) -> datetime.datetime:
        _, path = cls._parse_path(path)

        return datetime.datetime.fromtimestamp(os.path.getmtime(path))

    @classmethod
    def _delete(cls, path: str) -> NoReturn:
        _, path = cls._parse_path(path)

        _log.debug('Deleting local file: "%s"', path)

        os.unlink(path)

    @classmethod
    def _objects_list(cls, path: str) -> List[str]:
        _, path = cls._parse_path(path)

        objects = glob.iglob(os.path.join(path, '*'))
        objects = [f'{cls._proto}://{obj}' for obj in objects]

        return objects

    @classmethod
    def _exists(cls, path: str) -> bool:
        _, path = cls._parse_path(path)

        return os.path.exists(path)

    @classmethod
    def _copy(cls, source: str, destination: str) -> NoReturn:
        _, source = cls._parse_path(source)
        _, destination = cls._parse_path(destination)

        target_dir = os.path.dirname(destination)

        if not os.path.exists(target_dir):
            _log.debug('Target directory "%s" does not exist, creating one(s)',
                       target_dir)
            os.makedirs(target_dir, 0o700)

        _log.debug('Copying local file "%s" to "%s"', source, destination)

        shutil.copy2(source, destination)
