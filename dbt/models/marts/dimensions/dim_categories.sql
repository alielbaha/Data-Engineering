{{ config(materialized='table') }}

select
    md5(lower(trim(category_name))) as category_key,
    trim(category_name) as category_name
from {{ ref('stg_playstore_apps') }}
where category_name is not null
  and trim(category_name) <> ''
group by 1, 2
