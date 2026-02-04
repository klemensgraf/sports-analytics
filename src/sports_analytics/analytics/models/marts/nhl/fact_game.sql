with games as (
  select
    game_id,
    cast(game_date as date) as game_date,
    season,
    game_type,
    upper(trim(home_team_abbrev)) as home_team_abbrev,
    upper(trim(away_team_abbrev)) as away_team_abbrev,
    cast(home_score as integer) as home_score,
    cast(away_score as integer) as away_score,
    went_to_ot_flag,
    went_to_so_flag
  from {{ ref('int_nhl_game_base') }}
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
    home.team_sk as home_team_sk,
    away.team_sk as away_team_sk,

    -- Scoring info
    g.home_score,
    g.away_score,
    g.went_to_ot_flag,
    g.went_to_so_flag
  from games g
  left join dim_date d
    on d.date = g.game_date
  left join dim_team home
    on home.team_abbrev = g.home_team_abbrev
  left join dim_team away
    on away.team_abbrev = g.away_team_abbrev
)

select * from final
