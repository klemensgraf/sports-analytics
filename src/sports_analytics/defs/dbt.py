import dagster as dg
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets

from sports_analytics.defs.project import dbt_project


class CustomizedDagsterDbtTranslator(DagsterDbtTranslator):
    def get_group_name(self, dbt_resource_props):
        """
        Return a group name for a dbt resource derived from its fully qualified name.
        
        Parameters:
            dbt_resource_props (dict): DBT resource properties containing an "fqn" key whose value is a list of path components.
        
        Returns:
            str: The second element of `fqn` if `fqn` has more than one element, otherwise the first element.
        """
        fqn = dbt_resource_props["fqn"]
        return fqn[1] if len(fqn) > 1 else fqn[0]

    def get_asset_key(self, dbt_resource_props):
        """
        Map dbt resource properties to a Dagster AssetKey, prefixing source assets with "raw_".
        
        Parameters:
            dbt_resource_props (dict): Dictionary of dbt resource properties; expected to contain at least "resource_type" and "name".
        
        Returns:
            dg.AssetKey: The AssetKey for the corresponding Dagster asset. For resources with "resource_type" equal to "source" the key is "raw_<name>"; otherwise returns the asset key derived from the provided properties.
        """
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
    """
    Run the dbt project and yield the dbt CLI execution stream.
    
    Parameters:
        context (dg.AssetExecutionContext): Dagster asset execution context for the run.
        dbt (DbtCliResource): DBT CLI resource used to execute dbt commands.
    
    Returns:
        generator: A generator that yields execution events produced by the dbt CLI run stream.
    """
    yield from dbt.cli(["run"], context=context).stream()