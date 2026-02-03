with source as (
  select * from {{ source("raw_standings", "raw_nhl_standings_now") }}
),

renamed as (
  select
    team_name_default as name,
    team_abbrev_default as abbrev,
    place_name_default as location,
    division_name,
    division_abbrev,
    conference_name,
    conference_abbrev
  from source
)

select * from renamed
