from __future__ import annotations
import base64
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, Generator, List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 10000


class MySQLClient:
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.batch_size = batch_size
        self._engine: Optional[Engine] = None

    def _get_engine(self) -> Engine:
        if self._engine is None:
            connection_string = (
                f"mysql+pymysql://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
                "?charset=utf8mb4"
            )
            self._engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={"connect_timeout": 30},
            )
        return self._engine

    def get_table_schema(self, table_name: str) -> List[dict]:
        engine = self._get_engine()
        query = text(
            """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :table
            ORDER BY ORDINAL_POSITION
            """
        )
        with engine.connect() as conn:
            result = conn.execute(query, {"db": self.database, "table": table_name})
            return [dict(row._mapping) for row in result]

    def get_current_watermark(self, table_name: str, watermark_col: str) -> Optional[Any]:
        engine = self._get_engine()
        query = text(f"SELECT MAX(`{watermark_col}`) AS max_val FROM `{table_name}`")
        with engine.connect() as conn:
            result = conn.execute(query)
            row = result.fetchone()
            if row is None:
                return None
            return row[0]

    def extract_incremental(
        self,
        table_name: str,
        watermark_col: str,
        last_watermark: Any,
        columns: Optional[List[str]] = None,
    ) -> Generator[List[dict], None, None]:
        engine = self._get_engine()
        cols = ", ".join(f"`{c}`" for c in columns) if columns else "*"

        # Capture the upper bound once before pagination starts so that rows
        # updated mid-extraction cannot shift the ORDER BY and cause skips/dupes.
        upper_watermark = self.get_current_watermark(table_name, watermark_col)

        if last_watermark is None and upper_watermark is None:
            where_clause = "1=1"
            params: dict = {}
        elif last_watermark is None:
            where_clause = f"`{watermark_col}` <= :upper_watermark"
            params = {"upper_watermark": upper_watermark}
        else:
            where_clause = (
                f"`{watermark_col}` > :last_watermark "
                f"AND `{watermark_col}` <= :upper_watermark"
            )
            params = {"last_watermark": last_watermark, "upper_watermark": upper_watermark}

        offset = 0
        while True:
            query = text(
                f"""
                SELECT {cols}
                FROM `{table_name}`
                WHERE {where_clause}
                ORDER BY `{watermark_col}` ASC
                LIMIT :limit OFFSET :offset
                """
            )
            run_params = {**params, "limit": self.batch_size, "offset": offset}
            with engine.connect() as conn:
                result = conn.execute(query, run_params)
                rows = result.fetchall()
                keys = list(result.keys())

            if not rows:
                break

            batch = [self._serialize_row(dict(zip(keys, row))) for row in rows]
            logger.info(
                "Fetched batch of %d rows from %s (offset=%d, upper_watermark=%s)",
                len(batch),
                table_name,
                offset,
                upper_watermark,
            )
            yield batch

            if len(rows) < self.batch_size:
                break

            offset += self.batch_size

    def extract_full(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        order_by: Optional[str] = None,
    ) -> Generator[List[dict], None, None]:
        engine = self._get_engine()
        cols = ", ".join(f"`{c}`" for c in columns) if columns else "*"
        order_clause = f"ORDER BY `{order_by}`" if order_by else "ORDER BY 1"

        offset = 0
        while True:
            query = text(
                f"""
                SELECT {cols}
                FROM `{table_name}`
                {order_clause}
                LIMIT :limit OFFSET :offset
                """
            )
            with engine.connect() as conn:
                result = conn.execute(query, {"limit": self.batch_size, "offset": offset})
                rows = result.fetchall()
                keys = list(result.keys())

            if not rows:
                break

            batch = [self._serialize_row(dict(zip(keys, row))) for row in rows]
            logger.info(
                "Full extract batch of %d rows from %s (offset=%d)",
                len(batch),
                table_name,
                offset,
            )
            yield batch

            if len(rows) < self.batch_size:
                break

            offset += self.batch_size

    def _serialize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        serialized: Dict[str, Any] = {}
        for key, value in row.items():
            if value is None:
                serialized[key] = None
            elif isinstance(value, (datetime,)):
                serialized[key] = value.isoformat()
            elif isinstance(value, date):
                serialized[key] = value.isoformat()
            elif isinstance(value, Decimal):
                serialized[key] = float(value)
            elif isinstance(value, bytes):
                serialized[key] = base64.b64encode(value).decode("utf-8")
            elif isinstance(value, (int, float, str, bool)):
                serialized[key] = value
            else:
                serialized[key] = str(value)
        return serialized

    def close(self) -> None:
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
            logger.info("MySQL connection pool disposed")
