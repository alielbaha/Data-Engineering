{{ config(materialized='view') }}

with src as (
    select *
    from read_json_auto('data/raw/ai_note_apps_with_reviews.json')
), exploded as (
    select
        cast(appId as varchar) as app_id,
        cast(title as varchar) as app_name,
        unnest(reviews) as review
    from src
)

select
    md5(coalesce(app_id, '') || '|' || coalesce(cast(review.reviewId as varchar), '')) as review_key,
    app_id,
    app_name,
    cast(review.reviewId as varchar) as review_id,
    cast(review.userName as varchar) as user_name,
    cast(review.userName as varchar) as username,
    try_cast(review.score as integer) as rating_score,
    try_cast(review.score as integer) as score,
    cast(review.content as varchar) as review_content,
    cast(review.content as varchar) as content,
    try_cast(review.thumbsUpCount as bigint) as thumbs_up_count,
    try_cast(review.thumbsUpCount as bigint) as thumbsupcount,
    try_cast(review.at as timestamp) as review_timestamp,
    try_cast(review.at as timestamp) as at
from exploded
where app_id is not null
  and cast(review.reviewId as varchar) is not null
