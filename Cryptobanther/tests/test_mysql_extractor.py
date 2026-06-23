from __future__ import annotations
import base64
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch, call
import pytest


class TestMySQLClient:
    def test_extract_incremental_yields_batches(self):
        from ingestion.mysql.client import MySQLClient

        mock_engine = MagicMock()
        mock_conn = MagicMock().__enter__.return_value

        rows_per_batch = 10000
        batch1 = [(i, "completed", Decimal("99.99"), "USD", i + 1, datetime(2024, 1, i % 28 + 1), datetime(2024, 1, i % 28 + 1)) for i in range(rows_per_batch)]
        batch2 = [(i + rows_per_batch, "pending", Decimal("49.99"), "EUR", i + 1, datetime(2024, 1, i % 28 + 1), datetime(2024, 1, i % 28 + 1)) for i in range(rows_per_batch)]
        batch3 = []

        result1 = MagicMock()
        result1.fetchall.return_value = batch1
        result1.keys.return_value = ["id", "status", "amount", "currency", "user_id", "created_at", "updated_at"]

        result2 = MagicMock()
        result2.fetchall.return_value = batch2
        result2.keys.return_value = ["id", "status", "amount", "currency", "user_id", "created_at", "updated_at"]

        result3 = MagicMock()
        result3.fetchall.return_value = batch3
        result3.keys.return_value = ["id", "status", "amount", "currency", "user_id", "created_at", "updated_at"]

        conn_ctx = MagicMock()
        conn_ctx.__enter__ = MagicMock(return_value=conn_ctx)
        conn_ctx.__exit__ = MagicMock(return_value=False)
        conn_ctx.execute.side_effect = [result1, result2, result3]

        mock_engine.connect.return_value = conn_ctx

        client = MySQLClient(host="localhost", port=3306, database="test", user="u", password="p", batch_size=rows_per_batch)
        client._engine = mock_engine

        batches = list(client.extract_incremental("transactions", "updated_at", last_watermark=None))

        assert len(batches) == 2
        assert len(batches[0]) == rows_per_batch
        assert len(batches[1]) == rows_per_batch

    def test_serialize_row_converts_types(self):
        from ingestion.mysql.client import MySQLClient

        client = MySQLClient(host="localhost", port=3306, database="test", user="u", password="p")
        raw_row = {
            "id": 1,
            "created_at": datetime(2024, 1, 15, 12, 30, 45),
            "birth_date": date(1990, 6, 20),
            "amount": Decimal("123.456"),
            "hash": b"\xde\xad\xbe\xef",
            "name": "Alice",
            "active": True,
            "count": 42,
            "ratio": 0.75,
            "empty": None,
        }

        result = client._serialize_row(raw_row)

        assert result["created_at"] == "2024-01-15T12:30:45"
        assert result["birth_date"] == "1990-06-20"
        assert result["amount"] == 123.456
        assert result["hash"] == base64.b64encode(b"\xde\xad\xbe\xef").decode("utf-8")
        assert result["name"] == "Alice"
        assert result["active"] is True
        assert result["count"] == 42
        assert result["ratio"] == 0.75
        assert result["empty"] is None

    def test_mysql_type_to_bq_type(self):
        from ingestion.mysql.schemas import mysql_type_to_bq_type

        assert mysql_type_to_bq_type("int") == "INTEGER"
        assert mysql_type_to_bq_type("INT") == "INTEGER"
        assert mysql_type_to_bq_type("bigint") == "INTEGER"
        assert mysql_type_to_bq_type("tinyint(1)") == "INTEGER"
        assert mysql_type_to_bq_type("varchar(255)") == "STRING"
        assert mysql_type_to_bq_type("text") == "STRING"
        assert mysql_type_to_bq_type("datetime") == "TIMESTAMP"
        assert mysql_type_to_bq_type("timestamp") == "TIMESTAMP"
        assert mysql_type_to_bq_type("date") == "DATE"
        assert mysql_type_to_bq_type("decimal(10,2)") == "FLOAT64"
        assert mysql_type_to_bq_type("float") == "FLOAT64"
        assert mysql_type_to_bq_type("boolean") == "BOOLEAN"
        assert mysql_type_to_bq_type("blob") == "BYTES"
        assert mysql_type_to_bq_type("json") == "STRING"
        assert mysql_type_to_bq_type("unknown_exotic_type") == "STRING"
