import dagster as dg
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager

from sports_analytics.utils.apis import EspnAPIResource


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
            "espn_api": EspnAPIResource(
                base_url=dg.EnvVar("ESPN_API_URL"), version="v2"
            ),
        }
    )
