import dagster as dg
from dagster_dbt import DbtCliResource
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager

from sports_analytics.defs.project import dbt_project
from sports_analytics.utils.apis import NhlAPIResource


@dg.definitions
def resources() -> dg.Definitions:
    """
    Create a Dagster Definitions object exposing runtime resources for the sports analytics project.
    
    The returned Definitions provides the following resources:
    - "duckdb": DuckDBResource configured from the DUCKDB_DATABASE environment variable.
    - "dbt": DbtCliResource configured with the repository's dbt project directory.
    - "io_manager": DuckDBPandasIOManager configured with the DUCKDB_DATABASE environment variable and schema "raw".
    - "nhl_api": NhlAPIResource configured from the NHL_API_BASE_URL environment variable.
    
    Returns:
        dg.Definitions: A Dagster Definitions containing the configured resources.
    """
    return dg.Definitions(
        resources={
            "duckdb": DuckDBResource(
                database=dg.EnvVar("DUCKDB_DATABASE"),
            ),
            "dbt": DbtCliResource(project_dir=dbt_project.project_dir),
            "io_manager": DuckDBPandasIOManager(
                database=dg.EnvVar("DUCKDB_DATABASE"), schema="raw"
            ),
            "nhl_api": NhlAPIResource(base_url=dg.EnvVar("NHL_API_BASE_URL")),
        }
    )