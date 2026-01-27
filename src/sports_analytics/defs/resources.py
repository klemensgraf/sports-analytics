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
    - "duckdb": DuckDBResource configured from the DUCKDB_DATABASE_{DEV,TEST,PROD} environment variable based on DBT_TARGET.
    - "dbt": DbtCliResource configured with the repository's dbt project directory.
    - "io_manager": DuckDBPandasIOManager configured with the DUCKDB_DATABASE_{DEV,TEST,PROD} environment variable and schema "raw".
    - "nhl_api": NhlAPIResource configured from the NHL_API_BASE_URL environment variable.

    Returns:
        dg.Definitions: A Dagster Definitions containing the configured resources.
    """
    dbt_target = dg.EnvVar("DBT_TARGET").get_value()
    valid_targets = {"dev", "test", "prod"}

    if dbt_target is None:
        dbt_target = "dev"  # Default to dev if not set
    elif dbt_target not in valid_targets:
        raise ValueError(
            f"Invalid DBT_TARGET '{dbt_target}'. Must be one of: {', '.join(sorted(valid_targets))}"
        )

    duckdb_env_var_name = {
        "dev": "DUCKDB_DATABASE_DEV",
        "test": "DUCKDB_DATABASE_TEST",
        "prod": "DUCKDB_DATABASE_PROD",
    }

    resources = {
        "duckdb": DuckDBResource(
            database=dg.EnvVar(duckdb_env_var_name[dbt_target]),
        ),
        "dbt": DbtCliResource(project_dir=dbt_project.project_dir),
        "io_manager": DuckDBPandasIOManager(
            database=dg.EnvVar(duckdb_env_var_name[dbt_target]), schema="raw"
        ),
        "nhl_api": NhlAPIResource(base_url=dg.EnvVar("NHL_API_BASE_URL")),
    }

    return dg.Definitions(resources=resources)
