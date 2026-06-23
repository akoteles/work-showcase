import datetime
import logging
import os
from typing import (
    List,
    NoReturn,
    Optional,
    Tuple,
)

from google.cloud.storage import Client
from google.cloud.storage.blob import Blob
from google.cloud.storage.bucket import Bucket

from ._core import FileObject

_log = logging.getLogger('GcpFileObject')
_env_checked = False


def _check_environment() -> NoReturn:
    global _env_checked

    if not _env_checked and 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        msg = ('Google application credentials are expected to be present '
               'in the environment. Set up the variable '
               '`GOOGLE_APPLICATION_CREDENTIALS` to point to a valid JSON '
               'token on a local filesystem and try again.')
        raise ValueError(msg)

    _env_checked = True


class GcpFileObject(FileObject):
    _proto = 'gs'

    def __init__(self, path: str):
        _check_environment()

        super(GcpFileObject, self).__init__(path)

        self._blob = self._get_blob(bucket_name=self._netloc,
                                    object_name=self._path)

        if not self._blob.exists():
            msg = 'Cannot operate on missing remote blob'
            _log.critical(msg)
            raise RuntimeError(msg)

    @classmethod
    def _remove_trailing_slash(cls, path: str) -> str:
        if len(path) > 0 and path[0] == '/':
            path = path[1:]

        return path

    @classmethod
    def _parse_path(cls, path: str) -> Tuple[str, str]:
        bucket_name, object_name = super()._parse_path(path)
        object_name = cls._remove_trailing_slash(object_name)

        return bucket_name, object_name

    @classmethod
    def _get_bucket(cls, *, path: Optional[str] = None,
                    bucket_name: Optional[str] = None) -> Bucket:
        if path is not None:
            assert bucket_name is None
            bucket_name, _ = cls._parse_path(path)
        elif bucket_name is not None:
            assert path is None
        else:
            raise ValueError('Either `path` or `bucket_name` should be '
                             'passed, not both or none of them')

        client = Client()
        bucket: Bucket = client.bucket(bucket_name)

        if not bucket.exists():
            msg = f'Bucket "{bucket_name}" does not exist'
            _log.error(msg)
            raise ValueError(msg)

        return bucket

    @classmethod
    def _get_blob(cls, *, path: Optional[str] = None,
                  bucket_name: Optional[str] = None,
                  bucket: Optional[Bucket] = None,
                  object_name: Optional[str] = None) -> Blob:
        if path is not None:
            assert bucket_name is None and \
                   bucket is None and \
                   object_name is None
            bucket_name, object_name = cls._parse_path(path)
        elif bucket_name is not None or \
                bucket is not None or \
                object_name is not None:
            assert path is None
        else:
            raise ValueError('Either `path` or pair of `bucket_name` and '
                             '`object_name` arguments should be passed, not '
                             'both or none of them')

        object_name = cls._remove_trailing_slash(object_name)

        if bucket is None:
            assert bucket_name is not None
            bucket = cls._get_bucket(bucket_name=bucket_name)

        blob = bucket.blob(object_name)

        return blob

    def _enter(self, tmp_dir: str) -> str:
        _check_environment()

        file_name = os.path.basename(self._path)
        local_file_name = os.path.join(tmp_dir, file_name)

        _log.debug('Downloading object "%s" from bucket "%s" to a local '
                   'file "%s"', self._path, self._netloc, local_file_name)

        with open(local_file_name, 'wb') as f:
            self._blob.download_to_file(f)

        return local_file_name

    def _exit(self, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    def _upload_object(cls, local_file_name: str, netloc: str, path: str,
                       force: bool = False) -> NoReturn:
        _check_environment()

        blob = cls._get_blob(bucket_name=netloc, object_name=path)

        if blob.exists():
            if not force:
                msg = f'Remote "{path}" exists in bucket "{netloc}". Use ' \
                      '`force=True` to overwrite it'
                _log.error(msg)
                raise RuntimeError(msg)
            else:
                _log.warning(f'Overwriting existing file object "{path}" in '
                             f'bucket "{netloc}"')

        _log.debug('Uploading local file "%s" to an object "%s" in a '
                   'bucket "%s"', local_file_name, path, netloc)

        with open(local_file_name, 'rb') as f:
            blob.upload_from_file(f)

    @classmethod
    def _creation_time(cls, path: str) -> datetime.datetime:
        _check_environment()

        blob = cls._get_blob(path=path)

        assert blob.exists()

        blob.reload()

        return blob.time_created

    @classmethod
    def _delete(cls, path: str) -> NoReturn:
        _check_environment()

        blob = cls._get_blob(path=path)

        _log.debug('Deleting object "%s" from bucket "%s"', blob.name,
                   blob.bucket.name)

        blob.delete()

    @classmethod
    def _objects_list(cls, path: str) -> List[str]:
        def _join_url(bucket_name: str, path: str) -> str:
            url = f'{cls._proto}://{bucket_name}'

            if len(path) > 0:
                if path[0] != '/':
                    url += '/'

            url += path

            return url

        _check_environment()

        bucket_name, path = cls._parse_path(path)

        if path == '/':
            path = None

        bucket = cls._get_bucket(bucket_name=bucket_name)
        blobs = [_join_url(bucket_name, blob.name)
                 for blob in bucket.list_blobs(prefix=path)]

        return blobs

    @classmethod
    def _exists(cls, path: str) -> bool:
        _check_environment()

        blob = cls._get_blob(path=path)

        return blob.exists()

    @classmethod
    def _copy(cls, source: str, destination: str) -> NoReturn:
        source_bucket_name, source_object_name = cls._parse_path(source)
        source_bucket = cls._get_bucket(bucket_name=source_bucket_name)
        source_blob = cls._get_blob(bucket=source_bucket,
                                    object_name=source_object_name)

        destination_bucket_name, destination_object_name = \
            cls._parse_path(destination)
        destination_bucket = cls._get_bucket(
            bucket_name=destination_bucket_name)

        _log.debug('Copying blob "%s" in bucket "%s" to blob "%s" in '
                   'bucket "%s"', source_object_name, source_bucket_name,
                   destination_object_name, destination_bucket_name)

        _ = source_bucket.copy_blob(source_blob, destination_bucket,
                                    destination_object_name)
