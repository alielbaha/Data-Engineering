# Run Instructions (Lab 2)

## 1) Environment

From project root:

```powershell
cd "c:\Users\lenovo\Desktop\data engineering github\Data-Engineering"
```

Install required packages on Python 3.9:

```powershell
py -3.9 -m pip install duckdb dbt-core dbt-duckdb flask matplotlib python-docx pypdf
```

## 2) dbt Profile

Make sure this file exists:

- `C:\Users\lenovo\.dbt\profiles.yml`

Example content:

```yaml
playstore_dbt:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: C:/Users/lenovo/Desktop/data engineering github/Data-Engineering/dbt/data/duckdb/playstore.duckdb
      threads: 4
      schema: main
```

## 3) Validate dbt Connection

```powershell
cd dbt
C:\Users\lenovo\AppData\Local\Programs\Python\Python39\Scripts\dbt.exe debug
```

## 4) Build the Pipeline

Run all models:

```powershell
C:\Users\lenovo\AppData\Local\Programs\Python\Python39\Scripts\dbt.exe run
```

Run all tests:

```powershell
C:\Users\lenovo\AppData\Local\Programs\Python\Python39\Scripts\dbt.exe test
```

Run snapshots (SCD2):

```powershell
C:\Users\lenovo\AppData\Local\Programs\Python\Python39\Scripts\dbt.exe snapshot
```

If you changed columns in incremental fact model, refresh once:

```powershell
C:\Users\lenovo\AppData\Local\Programs\Python\Python39\Scripts\dbt.exe run --full-refresh --select +fact_reviews
```

## 5) Launch Advanced Dashboard (Flask)

From repo root:

```powershell
py -3.9 dbt\scripts\advanced_dashboard.py
```

Open:

- `http://127.0.0.1:5050`

## 6) Generate Static Visuals (PNG)

```powershell
py -3.9 dbt\scripts\generate_lab2_visuals.py
```

Generated files:

- `images/rating_trend.png`
- `images/app_performance.png`
- `images/worst_apps.png`

## 7) Useful Selective Runs

Staging only:

```powershell
C:\Users\lenovo\AppData\Local\Programs\Python\Python39\Scripts\dbt.exe run --select stg_playstore_apps stg_playstore_reviews
```

Dimensions + fact:

```powershell
C:\Users\lenovo\AppData\Local\Programs\Python\Python39\Scripts\dbt.exe run --select dim_developers dim_categories dim_date dim_apps_scd fact_reviews
```

Serving only:

```powershell
C:\Users\lenovo\AppData\Local\Programs\Python\Python39\Scripts\dbt.exe run --select srv_monthly_rating_trend srv_developer_performance
```
