{{ config(materialized='table') }}

with src as (
    select *
    from {{ ref('apps_scd_snapshot') }}
)

select
    md5(src.app_id || '|' || cast(src.dbt_valid_from as varchar)) as app_version_key,
    md5(src.app_id) as app_key,
    src.app_id,
    src.title as app_name,
    dev.developer_key,
    cat.category_key,
    src.app_score,
    src.ratings,
    src.installs,
    src.price,
    src.dbt_valid_from,
    src.dbt_valid_to,
    case when src.dbt_valid_to is null then true else false end as is_current
from src
join {{ ref('dim_developers') }} dev
  on lower(trim(src.developer_name)) = lower(trim(dev.developer_name))
join {{ ref('dim_categories') }} cat
  on lower(trim(src.category_name)) = lower(trim(cat.category_name))
