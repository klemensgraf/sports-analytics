from pathlib import Path

import dagster as dg
from dagster_dbt import DbtProject

target = dg.EnvVar("DBT_TARGET").get_value()
if target is None:
    target = "dev"

dbt_project = DbtProject(
    project_dir=Path(__file__).parent.parent / "analytics",
    target=target,
)

dbt_project.prepare_if_dev()
