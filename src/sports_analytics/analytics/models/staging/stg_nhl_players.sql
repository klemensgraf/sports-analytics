select *
from {{ source("raw_players", "nhl_players") }}
