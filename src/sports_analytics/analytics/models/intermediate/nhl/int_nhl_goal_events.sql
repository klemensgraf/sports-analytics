with goals as (
  select
    game_id,
    goal_idx,
    period,
    period_type,
    time_in_period,
    scorer_player_id,
    scorer_first_name,
    scorer_last_name,
    team_abbrev,
    strength,
    home_score,
    away_score,
    goals_to_date
  from {{ ref('stg_nhl_game_goals') }}
),

games as (
  select
    game_id,
    home_team_id,
    home_team_abbrev,
    away_team_id,
    away_team_abbrev,
    game_date,
    season,
    game_type
  from {{ ref('stg_nhl_games') }}
),

enriched as (
  select
    g.game_id,
    g.goal_idx,

    -- Game info
    games.season,
    games.game_type,
    games.game_date,
    g.strength,
    g.home_score,
    g.away_score,

    -- Period and game time
    g.period,
    g.period_type,
    g.time_in_period,

    -- Team info
    g.team_abbrev,
    case
      when g.team_abbrev = games.home_team_abbrev then games.home_team_id
      when g.team_abbrev = games.away_team_abbrev then games.away_team_id
      else null
    end as team_id,

    -- Scorer info
    g.scorer_player_id,
    g.scorer_first_name,
    g.scorer_last_name,
    g.goals_to_date
  from goals g
  left join games using (game_id)
)

select * from enriched
