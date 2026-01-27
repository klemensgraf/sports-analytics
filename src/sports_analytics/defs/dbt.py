import dagster as dg
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets

from sports_analytics.defs.project import dbt_project


class CustomizedDagsterDbtTranslator(DagsterDbtTranslator):
    def get_group_name(self, dbt_resource_props):
        """Groups assets into different model categories"""
        fqn = dbt_resource_props["fqn"]
        return fqn[1] if len(fqn) > 1 else fqn[0]

    def get_asset_key(self, dbt_resource_props):
        """Transforms asset keys to match Dagster managed raw data assets"""
        resource_type = dbt_resource_props["resource_type"]
        name = dbt_resource_props["name"]

        if resource_type == "source":
            return dg.AssetKey(f"raw_{name}")
        else:
            return super().get_asset_key(dbt_resource_props)


@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=CustomizedDagsterDbtTranslator(),
)
def dbt_analytics(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["run"], context=context).stream()
