import dagster as dg
import pandas as pd
from dagster_duckdb import DuckDBResource
from pandas import json_normalize

from sports_analytics.defs.nhl.partitions import games_daily_partition
from sports_analytics.utils.apis import NhlAPIResource
from sports_analytics.utils.helpers import remove_existing_partition, to_snake_case


@dg.asset(
    metadata={"partition_expr": "partition_key"},
    group_name="raw",
    kinds={"python"},
    partitions_def=games_daily_partition,
)
def raw_nhl_games_final(
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


@dg.asset(group_name="raw", kinds={"python"})
def raw_nhl_standings_now(
    context: dg.AssetExecutionContext, nhl_api: NhlAPIResource
) -> pd.DataFrame:
    """Get current standings and basic team stats"""
    # Calling API endpoint
    url = "/standings/now"
    result = nhl_api.get(url)

    # Flatten raw data
    standings = json_normalize(result.get("standings", []), sep="_")

    # Converting column name to snake case
    standings.columns = [to_snake_case(c) for c in standings.columns]

    return pd.DataFrame(standings)


@dg.asset(deps=["raw_nhl_standings_now"], group_name="raw", kinds={"python"})
def raw_nhl_players(
    context: dg.AssetExecutionContext, duckdb: DuckDBResource, nhl_api: NhlAPIResource
) -> pd.DataFrame:
    """Get all players from each team's roster"""
    table_name = "nhl_standings_now"
    schema = context.resources.io_manager._schema
    query = f"""
        select team_abbrev_default, team_name_default
        from {schema}.{table_name}
    """

    # Get each team's abbreviation and name
    with duckdb.get_connection() as conn:
        teams = conn.execute(query).fetchall()

    # List to store all rosters in
    rosters: list[pd.DataFrame] = []

    for team_abbrev, team_name in teams:
        # Call API endpoint for each team
        url = f"/roster/{team_abbrev}/current"
        result = nhl_api.get(url)

        # Get JSON data for all positions
        forwards = pd.DataFrame(json_normalize(result.get("forwards", []), sep="_"))
        defensemen = pd.DataFrame(json_normalize(result.get("defensemen", []), sep="_"))
        goalies = pd.DataFrame(json_normalize(result.get("goalies", []), sep="_"))

        # Concat all positions to one DataFrame
        roster = pd.concat([forwards, defensemen, goalies])
        roster["team_name"] = team_name
        roster["team_abbrev"] = team_abbrev

        # Convert column name to snake case
        roster.columns = [to_snake_case(c) for c in roster.columns]

        # Add roster to a list to concat on all teams afterwards
        rosters.append(roster)

    # Return all players from each's team roster
    return pd.concat(rosters)
