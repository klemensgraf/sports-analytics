with bounds as (
  select
    min(cast(game_date as date)) as min_date,
    max(cast(game_date as date)) as max_date
  from {{ ref('stg_nhl_games') }}
),

dates as (
  select
    cast(d as date) as date_day
  from bounds
  -- generate 1 row per day from min to max (inclusive)
  cross join generate_series(min_date, max_date, interval 1 day) as t(d)
),

final as (
  select
    -- Date surrogate key as yyyymmdd integer
    cast(strftime('%Y%m%d', date_day) as integer) as date_sk,
    date_day as date,

    -- Split date into separate units
    cast(strftime('%Y', date_day) as integer) as year,
    cast(strftime('%m', date_day) as integer) as month,
    cast(strftime('%d', date_day) as integer) as day,

    -- Week of year and day of week
    cast(strftime('%W', date_day) as integer) as week_of_year,
    -- 0=Sunday ... 6=Saturday
    cast(strftime('%w', date_day) as integer) as day_of_week,

    case
      when cast(strftime('%w', date_day) as integer) in (0, 6) then true
      else false
    end as is_weekend_flag
  from dates
)

select * from final
