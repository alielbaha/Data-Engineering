{{ config(materialized='table') }}

select
    md5(lower(trim(developer_name))) as developer_key,
    trim(developer_name) as developer_name
from {{ ref('stg_playstore_apps') }}
where developer_name is not null
  and trim(developer_name) <> ''
group by 1, 2
