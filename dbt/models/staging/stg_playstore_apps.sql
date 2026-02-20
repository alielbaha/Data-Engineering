{{ config(materialized='view') }}

with src as (
    select *
    from read_json_auto('data/raw/ai_note_apps_with_reviews.json')
)

select
    md5(coalesce(cast(appId as varchar), '')) as app_key,
    cast(appId as varchar) as app_id,
    cast(title as varchar) as app_name,
    cast(title as varchar) as title,
    cast(developer as varchar) as developer_name,
    cast(developer as varchar) as developer,
    cast(genre as varchar) as category_name,
    cast(genre as varchar) as genre,
    try_cast(score as double) as app_score,
    try_cast(score as double) as score,
    coalesce(array_length(reviews), 0)::bigint as ratings,
    coalesce(try_cast(replace(replace(cast(installs as varchar), ',', ''), '+', '') as bigint), 0) as installs,
    coalesce(try_cast(price as double), 0.0) as price
from src
where appId is not null
