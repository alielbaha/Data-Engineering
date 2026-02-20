{{ config(materialized='table') }}

with bounds as (
    select
        min(cast(review_timestamp as date)) as min_date,
        max(cast(review_timestamp as date)) as max_date
    from {{ ref('stg_playstore_reviews') }}
), date_spine as (
    select
        cast(gs.date_day as date) as full_date
    from bounds,
    generate_series(bounds.min_date, bounds.max_date, interval 1 day) as gs(date_day)
)

select
    cast(strftime(full_date, '%Y%m%d') as integer) as date_key,
    full_date,
    extract(year from full_date) as year,
    extract(month from full_date) as month,
    extract(day from full_date) as day,
    extract(quarter from full_date) as quarter,
    cast(strftime(full_date, '%W') as integer) as week_of_year,
    strftime(full_date, '%A') as day_name,
    case when strftime(full_date, '%w') in ('0', '6') then true else false end as is_weekend
from date_spine
order by full_date
