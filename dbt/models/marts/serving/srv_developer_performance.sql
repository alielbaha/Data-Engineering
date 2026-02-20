{{ config(materialized='table') }}

select
    dev.developer_key,
    dev.developer_name,
    count(*) as review_count,
    round(avg(f.rating_score), 4) as avg_rating,
    round(100.0 * sum(case when f.rating_score <= 2 then 1 else 0 end) / nullif(count(*), 0), 2) as low_rating_pct,
    round(avg(f.thumbs_up_count), 4) as avg_thumbs_up,
    min(f.review_timestamp) as first_review_ts,
    max(f.review_timestamp) as last_review_ts
from {{ ref('fact_reviews') }} f
join {{ ref('dim_developers') }} dev
  on f.developer_key = dev.developer_key
group by 1, 2
order by review_count desc, avg_rating desc
