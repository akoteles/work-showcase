"""MySQL utility module."""
import logging

from typing import (
    Any,
    Optional,
)

import mysql.connector

_log = logging.getLogger(__name__)


class MySqlConnection(object):
    def __init__(self, host: str, port: Optional[int] = None,
                 user: Optional[str] = None, password: Optional[str] = None,
                 database_name: Optional[str] = None):
        self._conn = mysql.connector.connect(host=host, port=port, user=user,
                                             password=password,
                                             database=database_name)

    def exec(self, stmt: str, *args) -> Any:
        cursor = self._conn.cursor()
        cursor.execute(stmt, *args)

        return cursor

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def __del__(self):
        self._conn.close()
