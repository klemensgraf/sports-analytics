with source as (
  select * from {{ source("raw_games", "raw_nhl_games_final") }}
),

renamed as (
  select
    id as game_id,
    season,
    game_type,
    game_date,
    start_time_utc,
    game_state,
    game_schedule_state,
    neutral_site,
    venue_default as venue,
    venue_timezone,
    away_team_id,
    away_team_name_default as away_team_name,
    away_team_abbrev,
    away_team_score,
    away_team_sog,
    home_team_id,
    home_team_name_default as home_team_name,
    home_team_abbrev,
    home_team_score,
    home_team_sog,
    clock_time_remaining,
    clock_seconds_remaining,
    clock_running,
    clock_in_intermission,
    period_descriptor_number as period_number,
    period_descriptor_period_type as period_type,
    game_outcome_last_period_type as last_period_type,
    _partition_key
  from source
)

select * from renamed
