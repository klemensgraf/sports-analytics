import dagster as dg
import pandas as pd
from dagster_duckdb import DuckDBResource
from pandas import json_normalize
from datetime import date

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
    """
    Fetch normalized NHL game records for the asset's partition date and prepare them for ingestion.

    This function calls the NHL score endpoint for the execution partition date, flattens the returned games into a pandas DataFrame with snake_case column names, adds a `partition_key` column, removes any existing data for the same partition via the provided DuckDB resource, and retains only rows where `game_state` equals "OFF".

    Returns:
        pd.DataFrame: DataFrame of normalized game records for the partition date; columns are in snake_case and include `partition_key`. Rows correspond to games with `game_state == "OFF"`.
    """
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

    return games


@dg.asset(group_name="raw", kinds={"python"})
def raw_nhl_standings_now(
    context: dg.AssetExecutionContext, nhl_api: NhlAPIResource
) -> pd.DataFrame:
    """
    Retrieve current NHL standings and basic team statistics.

    Returns:
        pd.DataFrame: A DataFrame of standings rows with column names converted to snake_case.
    """
    # Calling API endpoint
    url = "/standings/now"
    result = nhl_api.get(url)

    # Flatten raw data
    standings = json_normalize(result.get("standings", []), sep="_")

    # Converting column name to snake case
    standings.columns = [to_snake_case(c) for c in standings.columns]

    # Adding current date as metadata
    standings["_loaded_at"] = date.today()

    return standings


@dg.asset(deps=["raw_nhl_standings_now"], group_name="raw", kinds={"python"})
def raw_nhl_players(
    context: dg.AssetExecutionContext, duckdb: DuckDBResource, nhl_api: NhlAPIResource
) -> pd.DataFrame:
    """
    Aggregate every NHL team's current roster into a single DataFrame.

    Queries the raw.nhl_standings_now table to obtain each team's abbreviation and name, calls the roster API for each team, concatenates players from all position groups, adds team_name and team_abbrev columns, and converts column names to snake_case.

    Returns:
        pd.DataFrame: A DataFrame containing all players from every team's current roster with team metadata and snake_case column names.
    """
    table_name = "raw_nhl_standings_now"
    schema = "raw"
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
        forwards = json_normalize(result.get("forwards", []), sep="_")
        defensemen = json_normalize(result.get("defensemen", []), sep="_")
        goalies = json_normalize(result.get("goalies", []), sep="_")

        # Concat all positions to one DataFrame
        roster = pd.concat([forwards, defensemen, goalies], ignore_index=True)
        roster["team_name"] = team_name
        roster["team_abbrev"] = team_abbrev

        # Convert column name to snake case
        roster.columns = [to_snake_case(c) for c in roster.columns]

        # Add roster to a list to concat on all teams afterwards
        rosters.append(roster)

    # Return all players from each's team roster
    return pd.concat(rosters, ignore_index=True)
