# Lab 2 - dbt + DuckDB Architecture

This README describes the final architecture implemented in this project for Lab 2.

## 1) End-to-End Architecture

```mermaid
flowchart LR
    S[Google Play API] --> I[src/scrapper.py]
    I --> R[data/raw/ai_note_apps_with_reviews.json]

    R --> STG[stg_playstore_apps + stg_playstore_reviews]
    STG --> DIM[dim_developers + dim_categories + dim_apps + dim_date]
    STG --> SCD[apps_scd_snapshot -> dim_apps_scd]

    DIM --> FACT[fact_reviews incremental]
    SCD --> FACT

    FACT --> SRV[srv_monthly_rating_trend + srv_developer_performance]
    SRV --> BI[Flask Dashboard + PNG Visuals]
```

## 2) Star/Snowflake View (Implemented)

```mermaid
flowchart TB
    DR[dim_developers]
    DC[dim_categories]
    DA[dim_apps]
    DD[dim_date]
    DAS[dim_apps_scd]
    FR[fact_reviews]

    DR --> DA
    DC --> DA
    DD --> FR
    DR --> FR
    DC --> FR
    DAS --> FR
```

## 3) Important Notes

- `fact_reviews` is **incremental** with `unique_key = review_id`.
- `apps_scd_snapshot` + `dim_apps_scd` implement **SCD Type 2**.
- dbt tests cover:
  - key uniqueness and non-null checks,
  - FK relationships across dimensions and facts,
  - domain checks on `rating_score`.
- Consumption outputs include:
  - serving tables (`srv_monthly_rating_trend`, `srv_developer_performance`),
  - interactive Flask dashboard,
  - PNG visuals (`images/`).
