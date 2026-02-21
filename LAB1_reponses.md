# Lab 1 - Reponses Adaptees au Projet

## A. Environment Setup
- Environnement Python utilise pour tous les scripts du pipeline.
- Librairies principales: `google_play_scraper`, `pandas`, `flask`, `matplotlib`.

## B1. Data Acquisition and Ingestion
- Source: Google Play via `src/scrapper.py`.
- Donnees extraites: metadata apps + reviews utilisateurs.
- Raw conserve sans logique metier dans `data/raw/ai_note_apps_with_reviews.json`.
- Limite actuelle: raw combine apps/reviews dans un seul fichier (pas encore separe en 2 fichiers raw distincts).

## B2. Diagnosing and Transforming Raw Data
- Inspection raw faite avant transformation (`inspect_raw_data`).
- Problemes identifies: structure imbriquee, types heterogenes, installs en texte, valeurs manquantes, timestamps non uniformes.
- Transformation vers 2 tables tabulaires:
  - `data/processed/apps_catalog.csv` -> `appId, title, developer, score, ratings, installs, genre, price`
  - `data/processed/apps_reviews.csv` -> `app_id, app_name, reviewId, userName, score, content, thumbsUpCount, at`
- Verification post-transfo:
  - tables tabulaires
  - join possible `appId <-> app_id`
  - champs numeriques convertis
  - aggregation journaliere possible
  - anomalies documentees

## B3. Serving Layer
- KPIs app-level implementes:
  - number_of_reviews
  - average_rating
  - %_low_rating_reviews (<= 2)
  - first_review_date
  - most_recent_review_date
- KPIs journaliers implementes:
  - daily_number_of_reviews
  - daily_average_rating

## B4. Lightweight Dashboarding
- Dashboard Flask + Matplotlib implemente.
- Repond aux questions:
  - apps les plus/moins performantes
  - tendance des ratings dans le temps
  - differences de volume de reviews entre apps

## C1. New Reviews Batch (`note_taking_ai_reviews_batch2.csv`)
- Pipeline execute en full refresh (rebuild complet des outputs).
- Deduplication des reviews sur `reviewId` (tri par timestamp, keep last).
- Reviews referencant des apps absentes: warning explicite.
- Point d'attention: comportement full refresh implicite (pas incremental dans Lab1).

## C2. Schema Drift in Reviews (`note_taking_ai_reviews_schema_drift.csv`)
- Constat: logique basee sur noms de colonnes attendus.
- Impact: schema drift peut casser le pipeline ou produire des sorties incorrectes si non mappe.
- Ce qui manque pour robustesse: couche de mapping/schema contract avant transformation.

## C3. Dirty and Inconsistent Data (`note_taking_ai_reviews_dirty.csv`)
- Gestion actuelle:
  - coercition des numeriques (`to_numeric(errors='coerce')`)
  - parsing datetime (`to_datetime(errors='coerce')`)
- Effet:
  - les invalides sont neutralises (NaN/0) selon les champs
  - certaines erreurs peuvent se propager dans les agregats si pas filtrees explicitement
- Amelioration recommandee: regles DQ strictes (drop/flag) avant serving.

## C4. Updated Applications Metadata (`note_taking_ai_apps_updated.csv`)
- Constat attendu: doublons app_id, valeurs manquantes et incoherences peuvent biaiser joins et KPIs.
- Dans notre version Lab1, ce cas n'est pas encore traite par un flux apps metadata dedie.
- Action cible: gerer unicite app_id + priorite des enregistrements + regles referentielles explicites.

## C5. New Business Logic (Sentiment vs Score)
- Sorties actuelles insuffisantes pour detecter contradiction texte/note.
- Extension proposee:
  - score sentiment heuristique (lexique positif/negatif)
  - flag `is_sentiment_rating_mismatch`
  - KPI mismatch par app et par jour

## Conclusion
- Lab1 est fonctionnel de bout en bout pour ingestion, transformation, verification, serving et dashboard.
- Fragilites identifiees: robustesse schema drift, gouvernance qualite dirty data, separation raw apps/reviews, et logique sentiment.
- Ces points ont motive la transition vers dbt + DuckDB en Lab2.
