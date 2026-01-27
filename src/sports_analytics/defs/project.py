from pathlib import Path

import dagster as dg
from dagster_dbt import DbtProject

dbt_project = DbtProject(
    project_dir=Path(__file__).parent.parent / "analytics",
    target=dg.EnvVar("DBT_TARGET").get_value() or "dev",
)

dbt_project.prepare_if_dev()
