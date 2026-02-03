with source as (
  select id, cast(goals as json) as goals_json, _partition_key
  from {{ source("raw_games", "raw_nhl_games_final") }}
),

-- Explode goals from game data
goals as (
  select
    s.id as game_id,
    cast(g.key as integer) as goal_idx,
    g.value as goal,
  from source s
  , lateral json_each(goals_json) as g
),

-- Explode assists from exploded goals
assists as (
  select
    game_id,
    goal_idx,
    cast(a.key as integer) as assist_idx,
    a.value as assist,
    goal,
  from goals
  , lateral json_each(json_extract(goal, '$.assists')) as a
),

-- Latest partition date
max_partition as (
  select max(cast(_partition_key as date)) as max_part_key
  from source
)

select
  game_id,
  goal_idx,
  cast(json_extract(goal, '$.playerId') as bigint) as scorer_player_id,
  -- Player info
  assist_idx,
  cast(json_extract(assist, '$.playerId') as bigint) as assist_player_id,
  json_extract_string(assist, '$.name.default') as assist_player_name,
  cast(json_extract(assist, '$.assistsToDate') as integer) as assists_to_date,

  cast(m.max_part_key as date) as _loaded_at
from assists
cross join max_partition m
