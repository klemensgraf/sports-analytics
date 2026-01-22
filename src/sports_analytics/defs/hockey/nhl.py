import dagster as dg
import pandas as pd
from dagster_duckdb import DuckDBResource
from pandas import json_normalize

from sports_analytics.defs.hockey.partitions import games_daily_partition
from sports_analytics.utils.apis import NhlAPIResource
from sports_analytics.utils.helpers import remove_existing_partition, to_snake_case


@dg.asset(
    metadata={"partition_expr": "partition_key"},
    group_name="raw",
    kinds={"python"},
    partitions_def=games_daily_partition,
)
def nhl_games_final(
    context: dg.AssetExecutionContext, nhl_api: NhlAPIResource, duckdb: DuckDBResource
) -> pd.DataFrame:
    """Get game info and stats for provided date"""
    partition_key = context.partition_key

    # Calling API endpoint and flatten data
    url = f"/score/{partition_key}"

    result = nhl_api.get(url)
    games = json_normalize(result.get("games", []), sep="_")

    # Remove pre-existing data for this partition
    remove_existing_partition(duckdb, context)

    # Converting columns names to snake case
    games.columns = [to_snake_case(c) for c in games.columns]

    # Adding `partition_key` to data
    games["partition_key"] = partition_key

    if len(games) > 0:
        # Filter for unfinished games and remove them
        games = games[games["game_state"] == "OFF"]

    return pd.DataFrame(games)
