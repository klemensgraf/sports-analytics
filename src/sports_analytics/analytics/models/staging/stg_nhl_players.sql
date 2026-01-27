with source as (
  select * from {{ source("raw_players", "raw_nhl_players") }}
),

renamed as (
  select
    id,
    first_name_default as first_name,
    last_name_default as last_name,
    sweater_number,
    position_code,
    shoots_catches,
    height_in_centimeters,
    weight_in_kilograms,
    birth_date::date as birth_date,
    birth_country,
    birth_city_default as birth_city,
    birth_state_province_default as birth_state_province,
    team_name,
    team_abbrev
  from source
)

select * from renamed
