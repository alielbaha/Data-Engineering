{{ config(materialized='table') }}

select
    d.year,
    d.month,
    cast(concat(d.year, '-', lpad(cast(d.month as varchar), 2, '0')) as varchar) as year_month,
    count(*) as review_count,
    round(avg(f.rating_score), 4) as avg_rating,
    round(avg(f.thumbs_up_count), 4) as avg_thumbs_up
from {{ ref('fact_reviews') }} f
join {{ ref('dim_date') }} d
  on f.date_key = d.date_key
group by 1, 2, 3
order by 1, 2
