with games as (
  select
    -- Keys / Grain
    game_id,

    -- Core context
    season,
    game_type,
    cast(game_date as date) as game_date,
    cast(start_time_utc as timestamp) as start_time_utc,
    game_state,
    game_schedule_state,
    neutral_site,
    venue,
    venue_timezone,

    -- Teams
    away_team_id,
    away_team_name,
    away_team_abbrev,
    cast(away_team_score as integer) as away_score,
    cast(away_team_sog as integer) as away_sog,

    home_team_id,
    home_team_name,
    home_team_abbrev,
    cast(home_team_score as integer) as home_score,
    cast(home_team_sog as integer) as home_sog,

    -- Game clock snapshot (for finished games typically 00:00 but if there's an OT goal it remains)
    clock_time_remaining,
    cast(clock_seconds_remaining as integer) as clock_seconds_remaining,
    cast(clock_running as boolean) as clock_running,
    cast(clock_in_intermission as boolean) as clock_in_intermission,

    -- Outcome helpers
    period_number,
    period_type,
    last_period_type,

    case
      when upper(last_period_type) = 'OT'
      then true
      else false
    end as went_to_ot_flag,

    case
      when upper(last_period_type) = 'SO'
      then true
      else false
    end as went_to_so_flag,

    case
      when home_score > away_score then home_team_id
      when home_score < away_score then away_team_id
      else null
    end as winning_team_id,

    case
      when home_score > away_score then 'HOME'
      when home_score < away_score then 'AWAY'
      else null
    end as winner_side
  from {{ ref('stg_nhl_games') }}
)

select * from games
