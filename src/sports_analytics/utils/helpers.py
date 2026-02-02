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
    """Change every string to snake casing"""
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
    """Removes pre-existing records from destination table with same partition key"""
    # Get metadata from context
    table_name = context.asset_key.path[-1]  # Gets asset key for table name
    schema = context.resources.io_manager._schema
    partition_key = context.partition_key

    try:
        with duckdb.get_connection() as conn:
            result = conn.execute(
                f"DELETE FROM {schema}.{table_name} WHERE _partition_key = '{partition_key}'"
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
    Parse a value that may contain a nested structure encoded as TEXT.

    The input typically comes from a Pandas Series loaded from DuckDB where a
    nested column (e.g. list/dict) was stored as TEXT. This function converts:

    - missing values (None/NaN/pd.NA) -> None
    - valid JSON strings -> Python objects via json.loads
    - Python-literal strings (e.g. "[{'a': 1}]" with single quotes) -> Python objects
      via ast.literal_eval
    - already-parsed objects (list/dict) -> returned unchanged

    Parameters
    ----------
    s : Any
        The input value (string, list, dict, or missing).

    Returns
    -------
    Any | None
        Parsed Python object, the original object if already parsed, or None if missing.

    Raises
    ------
    ValueError, SyntaxError
        If parsing fails for both JSON and Python literal formats.
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
    except Exception:
        return ast.literal_eval(s)
