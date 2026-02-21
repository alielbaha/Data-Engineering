# Lab 2 - dbt + DuckDB Architecture

This README describes the final architecture implemented in this project for Lab 2.

## 1) End-to-End Architecture

```mermaid
flowchart LR
    A[Google Play API] -->|src/scrapper.py| B[Raw JSON]
    B --> C[dbt staging views]
    C --> D[Core dimensions]
    C --> E[dbt snapshot SCD2]
    E --> F[dim_apps_scd]
    D --> G[fact_reviews incremental]
    F --> G
    G --> H[Serving marts]
    H --> I[BI / Dashboard / PNG Visuals]

    subgraph Project Files
      B1["dbt/data/raw/ai_note_apps_with_reviews.json"]
      C1["models/staging/stg_playstore_apps.sql"]
      C2["models/staging/stg_playstore_reviews.sql"]
      D1["models/marts/dimensions/dim_developers.sql"]
      D2["models/marts/dimensions/dim_categories.sql"]
      D3["models/marts/dimensions/dim_apps.sql"]
      D4["models/marts/dimensions/dim_date.sql"]
      E1["snapshots/apps_scd_snapshot.sql"]
      F1["models/marts/dimensions/dim_apps_scd.sql"]
      G1["models/marts/facts/fact_reviews.sql"]
      H1["models/marts/serving/srv_monthly_rating_trend.sql"]
      H2["models/marts/serving/srv_developer_performance.sql"]
      I1["dbt/scripts/advanced_dashboard.py"]
      I2["dbt/scripts/generate_lab2_visuals.py"]
    end
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
