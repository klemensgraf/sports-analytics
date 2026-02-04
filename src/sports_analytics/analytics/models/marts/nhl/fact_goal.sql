with goals as (
  select
    game_id,
    goal_idx,
    cast(game_date as date) as game_date,
    upper(trim(team_abbrev)) as team_abbrev,
    scorer_player_id,
    strength,
    period,
    time_in_period
  from {{ ref('int_nhl_goal_events') }}
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

dim_player as (
  select
    player_sk,
    player_id
  from {{ ref('dim_player') }}
),

final as (
  select
    -- Game info
    g.game_id,
    g.goal_idx,
    d.date_sk,

    -- Team info
    t.team_sk,

    -- Scorer info
    p.player_sk as scorer_player_sk,

    g.strength,
    g.period,
    g.time_in_period
  from goals g
  left join dim_date d
    on d.date = g.game_date
  left join dim_team t
    on t.team_abbrev = g.team_abbrev
  left join dim_player p
    on p.player_id = g.scorer_player_id
)

select * from final
