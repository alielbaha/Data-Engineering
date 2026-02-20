{{
  config(
    materialized='incremental',
    unique_key='review_id'
  )
}}

with reviews as (
    select
        review_key,
        review_id,
        app_id,
        rating_score,
        thumbs_up_count,
        review_timestamp
    from {{ ref('stg_playstore_reviews') }}
    {% if is_incremental() %}
      where review_timestamp > (
          select coalesce(max(review_timestamp), cast('1900-01-01' as timestamp))
          from {{ this }}
      )
    {% endif %}
), apps as (
    select
        app_key,
        app_id,
        developer_key,
        category_key
    from {{ ref('dim_apps') }}
), dates as (
    select
        date_key,
        full_date
    from {{ ref('dim_date') }}
)

select
    r.review_key,
    r.review_id,
    a.app_key,
    a.developer_key,
    a.category_key,
    d.date_key,
    r.rating_score,
    r.thumbs_up_count,
    r.review_timestamp
from reviews r
join apps a
  on r.app_id = a.app_id
join dates d
  on cast(r.review_timestamp as date) = d.full_date
where a.app_key is not null
  and a.developer_key is not null
  and a.category_key is not null
  and d.date_key is not null
