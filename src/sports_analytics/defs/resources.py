import dagster as dg
from dagster_dbt import DbtCliResource
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager

from sports_analytics.defs.project import dbt_project
from sports_analytics.utils.apis import NhlAPIResource


@dg.definitions
def resources() -> dg.Definitions:
    return dg.Definitions(
        resources={
            "duckdb": DuckDBResource(
                database=dg.EnvVar("DUCKDB_DATABASE"),
            ),
            "dbt": DbtCliResource(project_dir=dbt_project),
            "io_manager": DuckDBPandasIOManager(
                database=dg.EnvVar("DUCKDB_DATABASE"), schema="raw"
            ),
            "nhl_api": NhlAPIResource(base_url=dg.EnvVar("NHL_API_BASE_URL")),
        }
    )
