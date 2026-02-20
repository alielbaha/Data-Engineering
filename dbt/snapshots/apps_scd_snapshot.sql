{% snapshot apps_scd_snapshot %}

{{
  config(
    target_schema='main',
    unique_key='app_id',
    strategy='check',
    check_cols=['title', 'developer_name', 'category_name', 'app_score', 'ratings', 'installs', 'price'],
    invalidate_hard_deletes=True
  )
}}

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

{% endsnapshot %}
