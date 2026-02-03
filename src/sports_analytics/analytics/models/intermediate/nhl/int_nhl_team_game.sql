with games as (
  select * from {{ ref('int_nhl_game_base') }}
),

team_game as (
  -- HOME row
  select
    -- Game info
    game_id,
    season,
    game_type,
    game_date,
    start_time_utc,

    -- Team info
    home_team_id as team_id,
    home_team_abbrev as team_abbrev,
    away_team_id as opponent_team_id,
    away_team_abbrev as opponent_team_abbrev,
    true as is_home_flag,

    -- Score stats
    home_score as goals_for,
    away_score as goals_against,
    home_score - away_score as goal_diff,

    case when home_score > away_score then true else false end as win_flag,
    case when home_score < away_score then true else false end as loss_flag
  from games

  union all

  -- Away row
  select
    -- Game info
    game_id,
    season,
    game_type,
    game_date,
    start_time_utc,

    -- Team info
    away_team_id as team_id,
    away_team_abbrev as team_abbrev,
    home_team_id as opponent_team_id,
    home_team_abbrev as opponent_team_abbrev,
    false as is_home_flag,

    away_score as goals_for,
    home_score as goals_against,
    away_score - home_score as goal_diff,

    case when away_score > home_score then true else false end as win_flag,
    case when away_score < home_score then true else false end as loss_flag
  from games
)

select * from team_game
