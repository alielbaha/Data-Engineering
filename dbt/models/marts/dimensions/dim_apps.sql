{{ config(materialized='table') }}

with apps as (
    select
        app_id,
        title,
        developer_name,
        category_name,
        app_score,
        ratings,
        installs,
        price
    from {{ ref('stg_playstore_apps') }}
)

select
    md5(apps.app_id) as app_key,
    apps.app_id,
    apps.title as app_name,
    dev.developer_key,
    cat.category_key,
    apps.app_score,
    apps.ratings,
    apps.installs,
    apps.price
from apps
join {{ ref('dim_developers') }} dev
  on lower(trim(apps.developer_name)) = lower(trim(dev.developer_name))
join {{ ref('dim_categories') }} cat
  on lower(trim(apps.category_name)) = lower(trim(cat.category_name))
