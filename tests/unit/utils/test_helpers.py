from unittest.mock import MagicMock

import pytest
from duckdb import CatalogException, DatabaseError

from sports_analytics.utils.helpers import remove_existing_partition, to_snake_case


# Test matrix -- input, expected output
@pytest.mark.parametrize(
    "input_str, expected",
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
def test_to_snake_case(input_str, expected):
    assert to_snake_case(input_str) == expected


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
            "DELETE FROM test_schema.test_table WHERE partition_key = '2026-01-21'"
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
