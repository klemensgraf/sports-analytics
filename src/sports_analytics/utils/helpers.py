import re

import dagster as dg
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


def remove_existing_partition(
    duckdb: DuckDBResource, context: dg.AssetExecutionContext
) -> None:
    """Removes pre-existing records from destination table with same partition key"""
    # Get metadata from context
    table_name = context.asset_key.path[-1]  # Gets asset key for table name
    schema = context.resources.io_manager._schema
    partition_key = context.partition_key

    try:
        with duckdb.get_connection() as conn:
            result = conn.execute(
                f"DELETE FROM {schema}.{table_name} WHERE partition_key = '{partition_key}'"
            ).fetchall()[0]
            context.log.info(
                f"Rows deleted with partition key '{partition_key}': {result[0]}"
            )
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
