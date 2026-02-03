from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
from duckdb import CatalogException, DatabaseError

from sports_analytics.utils.helpers import (
    parse_nested_datatype,
    remove_existing_partition,
    to_snake_case,
)


class TestToSnakeCase:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("PascalCase", "pascal_case"),
            ("camelCase", "camel_case"),
            ("kebab-case-string", "kebab_case_string"),
            ("dot.notation.test", "dot_notation_test"),
            ("HTTPResponseCode", "http_response_code"),
            ("User.Profile-Settings Data", "user_profile_settings_data"),
            ("V3.0IsReady", "v3_0_is_ready"),
            ("already_snake_case", "already_snake_case"),
            ("   LeadingAndTrailing   ", "leading_and_trailing"),
            ("Multiple___Underscores", "multiple_underscores"),
        ],
    )
    def test_to_snake_case(self, value, expected):
        assert to_snake_case(value) == expected


class TestRemoveExistingPartition:
    def test_successful_deletion(self, mock_duckdb, mock_io_manager, mock_context):
        """Should return row count and success status when deletion succeeds"""
        # Mock return value from DuckDB delete statement
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [(6,)]
        mock_duckdb.get_connection.return_value.__enter__.return_value = mock_conn

        remove_existing_partition(mock_duckdb, mock_context)

        # Assertions
        mock_conn.execute.assert_called_once_with(
            'DELETE FROM "test_schema"."test_table" WHERE _partition_key = ?',
            ["2026-01-21"],
        )
        mock_context.log.info.assert_called_once_with(
            "Rows deleted with partition key '2026-01-21': 6"
        )
        mock_context.log.warning.assert_not_called()

    def test_zero_rows_deleted(self, mock_duckdb, mock_context):
        """Should return 0 when no matching rows exist"""
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [(0,)]
        mock_duckdb.get_connection.return_value.__enter__.return_value = mock_conn

        remove_existing_partition(mock_duckdb, mock_context)

        mock_context.log.info.assert_called_once_with(
            "Rows deleted with partition key '2026-01-21': 0"
        )

    def test_table_does_not_exist(self, mock_duckdb, mock_context):
        """Should return warning when table doesn't exist"""
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = CatalogException("Table does not exist")
        mock_duckdb.get_connection.return_value.__enter__.return_value = mock_conn

        remove_existing_partition(mock_duckdb, mock_context)

        mock_context.log.warning.assert_called_once_with(
            "Table test_table in schema test_schema didn't exist"
        )
        mock_context.log.info.assert_not_called()

    def test_database_does_not_exist(self, mock_duckdb, mock_context):
        """Should raise DatabaseError for failing to remove records"""
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = CatalogException(
            "Database is in read-only mode"
        )
        mock_duckdb.get_connection.return_value.__enter__.return_value = mock_conn

        with pytest.raises(DatabaseError) as exc_info:
            remove_existing_partition(mock_duckdb, mock_context)

        assert "Failed to remove pre-existing records" in str(exc_info.value)

        # Verify no logging happened before the exception
        mock_context.log.info.assert_not_called()
        mock_context.log.warning.assert_not_called()

    def test_unexpected_exception_raises_fatal(self, mock_duckdb, mock_context):
        """Should raise RuntimeError for unexpected errors"""
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = RuntimeError("Connection Failed")
        mock_duckdb.get_connection.return_value.__enter__.return_value = mock_conn

        with pytest.raises(RuntimeError) as exc_info:
            remove_existing_partition(mock_duckdb, mock_context)

        assert "Failed to remove pre-existing records" in str(exc_info.value)


class TestParseNestedDatatype:
    @pytest.mark.parametrize(
        "value, expected",
        [
            # missing values
            (None, None),
            (float("nan"), None),
            (np.nan, None),
            (np.float64("nan"), None),
            (pd.NA, None),
            ("", None),
            ("   ", None),
            ("null", None),
            ("NULL", None),
            (" NuLl  ", None),
            # valid JSON
            ('{"a": 1, "b": [1, 2]}', {"a": 1, "b": [1, 2]}),
            ("[1, 2, 3]", [1, 2, 3]),
            ('"hello"', "hello"),
            ("true", True),
            ("false", False),
            ("123", 123),
            ("3.14", 3.14),
            ("[null, 1]", [None, 1]),
            # python-literal fallback (single quotes etc.)
            ("[{'a': 1}, {'b': 2}]", [{"a": 1}, {"b": 2}]),
            ("{'x': 'y'}", {"x": "y"}),
            ("(1, 2, 3)", (1, 2, 3)),
            ("None", None),  # ast.literal_eval handles this
            ("True", True),
        ],
    )
    def test_parses_expected(self, value, expected):
        assert parse_nested_datatype(value) == expected

    def test_returns_same_list_object(self):
        obj = [1, {"a": 2}]
        out = parse_nested_datatype(obj)
        assert out is obj

    def test_returns_same_dict_object(self):
        obj = {"a": [1, 2]}
        out = parse_nested_datatype(obj)
        assert out is obj

    @pytest.mark.parametrize("value", [5, 5.5, True, object()])
    def test_non_string_non_missing_returns_as_is(self, value):
        assert parse_nested_datatype(value) is value

    @pytest.mark.parametrize(
        "value",
        [
            "{bad json}",  # neither json nor literal eval
            "[1, 2, ",  # syntax error
            "not a structure",  # invalid literal
        ],
    )
    def test_invalid_strings_raise(self, value):
        with pytest.raises((ValueError, SyntaxError)):
            parse_nested_datatype(value)
