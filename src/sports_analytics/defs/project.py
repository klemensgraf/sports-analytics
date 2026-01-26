from pathlib import Path

import dagster as dg
from dagster_dbt import DbtProject

dbt_project = DbtProject(
    project_dir=Path(__file__).joinpath("../..", "analytics").resolve(),
    target=dg.EnvVar("DBT_TARGET").get_value(),
)

dbt_project.prepare_if_dev()
