with team_game as (
  select
    game_id,
    cast(game_date as date) as game_date,
    season,
    game_type,
    upper(trim(team_abbrev)) as team_abbrev,
    upper(trim(opponent_team_abbrev)) as opponent_team_abbrev,
    is_home_flag,
    cast(goals_for as integer) as goals_for,
    cast(goals_against as integer) as goals_against,
    cast(goal_diff as integer) as goal_diff,
    win_flag
  from {{ ref('int_nhl_team_game') }}
),

dim_team as (
  select
    team_sk,
    team_abbrev
  from {{ ref('dim_team') }}
),

dim_date as (
  select
    date_sk,
    date
  from {{ ref('dim_date') }}
),

final as (
  select
    -- Game info
    g.game_id,
    d.date_sk,
    g.season,
    g.game_type,

    -- Team info
    team.team_sk as team_sk,
    opponent.team_sk as opponent_team_sk,
    g.is_home_flag,

    -- Scoring info
    g.goals_for,
    g.goals_against,
    g.goal_diff,

    -- Game outcome
    g.win_flag
  from team_game g
  left join dim_date d
    on d.date = g.game_date
  left join dim_team team
    on team.team_abbrev = g.team_abbrev
  left join dim_team opponent
    on opponent.team_abbrev = g.opponent_team_abbrev
)

select * from final
