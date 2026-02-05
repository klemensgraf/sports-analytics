import dagster as dg

from sports_analytics.defs.nhl.partitions import games_daily_partition

nhl_update_job = dg.define_asset_job(
    name="nhl_update_job", partitions_def=games_daily_partition, selection='group:"raw"+'
)

nhl_update_job_daily = dg.build_schedule_from_partitioned_job(
    job=nhl_update_job, hour_of_day=9, minute_of_hour=0
)
