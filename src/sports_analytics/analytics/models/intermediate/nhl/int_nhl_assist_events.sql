with assists as (
  select
    game_id,
    goal_idx,
    scorer_player_id,
    assist_idx,
    assist_player_id,
    assist_player_name,
    assists_to_date
  from {{ ref('stg_nhl_game_assists') }}
),

goal_events as (
  select
    game_id,
    goal_idx,
    team_id,
    team_abbrev,
    season,
    game_type,
    game_date,
    period,
    period_type,
    time_in_period,
    strength
  from {{ ref('int_nhl_goal_events') }}
),

final as (
  select
    -- Game info
    a.game_id,
    a.goal_idx,
    a.assist_idx,

    -- Scoring info
    a.scorer_player_id,
    a.assist_player_id,
    a.assist_player_name,
    a.assists_to_date,

    -- Event and goal info
    ge.team_id,
    ge.team_abbrev,
    ge.season,
    ge.game_type,
    ge.game_date,
    ge.period,
    ge.period_type,
    ge.time_in_period,
    ge.strength
  from assists a
  left join goal_events ge
    using (game_id, goal_idx)
)

select * from final
