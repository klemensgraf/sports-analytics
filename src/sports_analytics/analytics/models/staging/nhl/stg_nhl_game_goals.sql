with source as (
  select id, cast(goals as json) as goals_json
  from {{ source("raw_games", "raw_nhl_games_final") }}
),

-- Explode nested JSON into rows for each goal
goals as (
  select
    s.id as game_id,
    cast(g.key as integer) as goal_idx,
    g.value as goal
  from source s
  , lateral json_each(goals_json) as g
)

select
  game_id,
  goal_idx,
  -- Period info
  cast(json_extract(goal, '$.period') as integer) as period,
  json_extract_string(goal, '$.periodDescriptor.periodType') as period_type,
  json_extract_string(goal, '$.timeInPeriod') as time_in_period,
  -- Player info
  cast(json_extract(goal, '$.playerId') as bigint) as scorer_player_id,
  json_extract_string(goal, '$.firstName.default') as scorer_first_name,
  json_extract_string(goal, '$.lastName.default') as scorer_last_name,
  -- Team info
  json_extract_string(goal, '$.teamAbbrev') as team_abbrev,
  json_extract_string(goal, '$.strength') as strength,
  -- Scoreboard
  cast(json_extract(goal, '$.homeScore') as integer) as home_score,
  cast(json_extract(goal, '$.awayScore') as integer) as away_score,
  cast(json_extract(goal, '$.goalsToDate') as integer) as goals_to_date
from goals
