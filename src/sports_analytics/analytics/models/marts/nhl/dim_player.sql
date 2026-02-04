with source as (
  select
    cast(player_id as bigint) as player_id,
    first_name,
    last_name,
    sweater_number,
    position_code,
    shoots_catches,
    height_cm,
    weight_kg,
    birth_date,
    birth_country,
    birth_city,
    birth_state_province,
    team_name,
    team_abbrev
  from {{ ref('stg_nhl_players') }}
),

final as (
  select
    -- Surrogate key based on player id
    {{ dbt_utils.generate_surrogate_key(['player_id']) }} as player_sk,

    -- Natural key
    player_id,

    -- Attributes
    first_name,
    last_name,
    sweater_number,
    position_code,
    shoots_catches,
    cast(height_cm as integer) as height_cm,
    cast(weight_kg as integer) as weight_kg,
    cast(birth_date as date) as birth_date,
    birth_country,
    birth_city,
    birth_state_province,

    -- Current team attributes (no history)
    team_name as current_team_name,
    upper(trim(team_abbrev)) as current_team_abbrev
  from source
)

select * from final
