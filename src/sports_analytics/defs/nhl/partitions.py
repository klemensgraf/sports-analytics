import dagster as dg

from sports_analytics.defs.nhl.constants import GAMES_START_DATE

games_daily_partition = dg.DailyPartitionsDefinition(
    start_date=GAMES_START_DATE, timezone="Europe/Zurich"
)
