import dagster as dg
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager

from sports_analytics.utils.apis import NhlAPIResource


@dg.definitions
def resources() -> dg.Definitions:
    return dg.Definitions(
        resources={
            "duckdb": DuckDBResource(
                database=dg.EnvVar("DUCKDB_DATABASE"),
            ),
            "io_manager": DuckDBPandasIOManager(
                database=dg.EnvVar("DUCKDB_DATABASE"), schema="raw"
            ),
            "nhl_api": NhlAPIResource(base_url=dg.EnvVar("NHL_API_BASE_URL")),
        }
    )
