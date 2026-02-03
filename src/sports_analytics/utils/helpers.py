import ast
import json
import re
from typing import Any

import dagster as dg
import numpy as np
import pandas as pd
from dagster_duckdb import DuckDBResource
from duckdb import CatalogException, DatabaseError


def to_snake_case(text: str) -> str:
    """
    Convert a string to snake_case.

    This helper normalizes common naming styles and separators:

    - replaces whitespace, dots and hyphens with underscores
    - inserts underscores between camelCase / PascalCase boundaries
      and in sequences like "HTTPResponse" -> "http_response"
    - lowercases the result
    - collapses multiple underscores and strips leading/trailing underscores

    Parameters:
        text : str
            Input string to normalize.

    Returns:
        str
            Normalized snake_case string.

    Examples:
        "PascalCase" -> "pascal_case"
        "kebab-case-string" -> "kebab_case_string"
        "User.Profile-Settings Data" -> "user_profile_settings_data"
    """
    # Replace all special chars with underscores
    s1 = re.sub(r"[.\-\s]+", "_", text)

    # Insert underscores before capital letters (Pascal and Camel casing)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    s2 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s2)

    # Change all letters to lower case
    s3 = s2.lower()

    # Clean double underscores
    s4 = re.sub(r"_+", "_", s3).strip("_")

    return s4


def remove_existing_partition(duckdb: DuckDBResource, context: dg.AssetExecutionContext) -> None:
    """
    Delete pre-existing rows for the current partition in the destination table.

    The target table is derived from the Dagster asset key (last path segment),
    the schema is read from the configured IO manager resource, and the
    partition key is taken from the execution context.

    Behavior:
        - Executes a DELETE statement filtered by `_partition_key`.
        - Logs an info message with the number of deleted rows.
        - If the table does not exist, logs a warning and returns.
        - If a DuckDB CatalogException occurs for other reasons, raises DatabaseError.
        - Any other unexpected exception is re-raised as RuntimeError.

    Parameters:
        duckdb : DuckDBResource
            DuckDB resource used to obtain a connection.
        context : dg.AssetExecutionContext
            Dagster context providing asset key, resources and partition key.

    Returns:
        None

    Raises:
        DatabaseError
            If deletion fails due to a DuckDB catalog-related error (except missing table).
        RuntimeError
            For any other unexpected error during deletion.
    """
    # Get metadata from context
    table_name = context.asset_key.path[-1]  # Gets asset key for table name
    schema = context.resources.io_manager._schema
    partition_key = context.partition_key

    try:
        with duckdb.get_connection() as conn:
            # Checks for safe table and schema name with quotation
            safe_schema = _quote_indent(schema)
            safe_table = _quote_indent(table_name)

            result = conn.execute(
                f"DELETE FROM {safe_schema}.{safe_table} WHERE _partition_key = ?", [partition_key]
            ).fetchall()[0]
            context.log.info(f"Rows deleted with partition key '{partition_key}': {result[0]}")
            return
    except CatalogException as e:
        if "does not exist" in str(e).lower():
            context.log.warning(f"Table {table_name} in schema {schema} didn't exist")
            return
        raise DatabaseError(
            f"Failed to remove pre-existing records from table: {schema}.{table_name}",
        ) from e

    except Exception as e:
        raise RuntimeError(
            f"Failed to remove pre-existing records from table: {schema}.{table_name}",
        ) from e


def parse_nested_datatype(s: Any) -> Any | None:
    """
    Parse a value that may represent a nested Python structure encoded as text.

    Converts missing or sentinel values to None, leaves already-parsed lists/dicts unchanged, and parses strings as JSON first, falling back to Python literal evaluation if JSON parsing fails.

    Parameters:
        s (Any): Input value which may be None, a numeric/sentinel, an already-parsed object, or a string encoding a nested structure.

    Returns:
        Any | None: The parsed Python object (list/dict/other), the original value if it is not a string and not a missing sentinel, or None for missing/null-like inputs.

    Raises:
        ValueError, SyntaxError: If the input is a string that cannot be parsed as valid JSON nor as a valid Python literal.
    """
    # Handle None quickly
    if s is None:
        return None

    # If it's already a nested Python object, keep it and return
    if isinstance(s, (list, dict)):
        return s

    # pd.isna on scalars returns bool; on list/array it returns array
    if isinstance(s, (float, np.floating)) and pd.isna(s):
        return None
    if s is pd.NA:
        return None

    # Only strings get parsed
    if not isinstance(s, str):
        # choose your policy: return as-is or None
        return s

    # Remove white space and check for null-strings
    s = s.strip()
    if s == "" or s.lower() == "null":
        return None

    # Parse JSON first, fallback to Python literal
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return ast.literal_eval(s)


def _quote_indent(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'
