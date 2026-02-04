with source as (
  select
    name,
    upper(trim(abbrev)) as team_abbrev,
    location,
    division_name,
    division_abbrev,
    conference_name,
    conference_abbrev
  from {{ ref('stg_nhl_teams') }}
),

final as (
  select
    -- Surrogate key based on team abbrev
    {{ dbt_utils.generate_surrogate_key(['team_abbrev']) }} as team_sk,

    -- Natural key
    team_abbrev,

    -- Attributes
    name as team_name,
    location as team_location,
    division_name,
    division_abbrev,
    conference_name,
    conference_abbrev
  from source
)

select * from final
