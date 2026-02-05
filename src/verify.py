import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_processed_data():
    """Load the processed datasets"""
    processed_dir = '../data/processed/'
    apps_df = pd.read_csv(os.path.join(processed_dir, 'apps_catalog.csv'))
    reviews_df = pd.read_csv(os.path.join(processed_dir, 'apps_reviews.csv'), parse_dates=['at'])

    return apps_df, reviews_df

def verify_tabular_consistency(apps_df, reviews_df):
    print("=== TABULAR CONSISTENCY VERIFICATION ===")

    print(f"Apps DataFrame shape: {apps_df.shape}")
    print(f"Reviews DataFrame shape: {reviews_df.shape}")
    print(f"Apps columns: {list(apps_df.columns)}")
    print(f"Reviews columns: {list(reviews_df.columns)}")

    apps_nested_cols = [col for col in apps_df.columns if apps_df[col].apply(lambda x: isinstance(x, (list, dict))).any()]
    reviews_nested_cols = [col for col in reviews_df.columns if reviews_df[col].apply(lambda x: isinstance(x, (list, dict))).any()]

    if apps_nested_cols:
        print(f"Issue: Apps still has nested structures in columns: {apps_nested_cols}")
    else:
        print("Apps dataset is fully tabular")

    if reviews_nested_cols:
        print(f"Issue: Reviews still has nested structures in columns: {reviews_nested_cols}")
    else:
        print("Reviews dataset is fully tabular")

def verify_join_capability(apps_df, reviews_df):
    print("\n=== JOIN CAPABILITY VERIFICATION ===")

    apps_join_keys = ['appId']
    reviews_join_keys = ['app_id']

    print(f"Apps join keys: {apps_join_keys}")
    print(f"Reviews join keys: {reviews_join_keys}")

    apps_missing_keys = [key for key in apps_join_keys if key not in apps_df.columns]
    reviews_missing_keys = [key for key in reviews_join_keys if key not in reviews_df.columns]

    if apps_missing_keys:
        print(f"Apps missing join keys: {apps_missing_keys}")
    else:
        print("All apps join keys present")

    if reviews_missing_keys:
        print(f"Reviews missing join keys: {reviews_missing_keys}")
    else:
        print("All reviews join keys present")

    try:
        merged = pd.merge(apps_df, reviews_df, left_on='appId', right_on='app_id', how='inner')
        print(f"Join successful: {merged.shape[0]} rows after joining")
        print(f"Example joined data shape: {merged.shape}")
    except Exception as e:
        print(f"Join failed: {e}")

def verify_numeric_fields(apps_df, reviews_df):
    print("\n=== NUMERIC FIELD VERIFICATION ===")

    apps_numeric_fields = ['score', 'ratings', 'installs', 'price']
    reviews_numeric_fields = ['score', 'thumbsUpCount']

    for field in apps_numeric_fields:
        if field in apps_df.columns:
            is_numeric = pd.api.types.is_numeric_dtype(apps_df[field])
            non_null_count = apps_df[field].notna().sum()
            print(f"Apps '{field}': numeric={is_numeric}, non-null={non_null_count}")

            if is_numeric:
                print(f"  - Min: {apps_df[field].min()}, Max: {apps_df[field].max()}")
                print(f"  - Mean: {apps_df[field].mean():.2f}")
        else:
            print(f"Apps missing expected numeric field: {field}")

    for field in reviews_numeric_fields:
        if field in reviews_df.columns:
            is_numeric = pd.api.types.is_numeric_dtype(reviews_df[field])
            non_null_count = reviews_df[field].notna().sum()
            print(f"Reviews '{field}': numeric={is_numeric}, non-null={non_null_count}")

            if is_numeric:
                print(f"  - Min: {reviews_df[field].min()}, Max: {reviews_df[field].max()}")
                print(f"  - Mean: {reviews_df[field].mean():.2f}")
        else:
            print(f"Reviews missing expected numeric field: {field}")

def verify_timestamp_aggregation(reviews_df):
    print("TIMESTAMP verification")

    if 'at' in reviews_df.columns:
        is_datetime = pd.api.types.is_datetime64_any_dtype(reviews_df['at'])
        print(f"Timestamp field 'at' is datetime: {is_datetime}")

        if is_datetime:
            reviews_df['date'] = reviews_df['at'].dt.date
            daily_counts = reviews_df.groupby('date').size()

            print(f"Successfully aggregated reviews by day")
            print(f"Number of days with reviews: {len(daily_counts)}")
            print(f"Day with most reviews: {daily_counts.idxmax()} ({daily_counts.max()} reviews)")
            print(f"Sample daily counts:\n{daily_counts.head()}")

            reviews_df['hour'] = reviews_df['at'].dt.hour
            hourly_dist = reviews_df['hour'].value_counts().sort_index()
            print(f"Hourly distribution available (sample): {hourly_dist.head()}")
        else:
            print("Timestamp field is not in datetime format")
    else:
        print("No timestamp field 'at' found in reviews")

def identify_anomalies(apps_df, reviews_df):
    print("\n=== ANOMALY DETECTION ===")

    anomalies = []

    if 'score' in apps_df.columns:
        score_outliers = apps_df[(apps_df['score'] < 0) | (apps_df['score'] > 5)]
        if not score_outliers.empty:
            anomalies.append(f"Apps with invalid scores: {len(score_outliers)} records")
            print(f"{len(score_outliers)} apps have invalid scores (outside 0-5 range)")
        else:
            print("All app scores are within valid range (0-5)")

    if 'installs' in apps_df.columns:
        negative_installs = apps_df[apps_df['installs'] < 0]
        if not negative_installs.empty:
            anomalies.append(f"Apps with negative installs: {len(negative_installs)} records")
            print(f"{len(negative_installs)} apps have negative install counts")
        else:
            print("All install counts are non-negative")

    if 'score' in reviews_df.columns:
        review_score_outliers = reviews_df[(reviews_df['score'] < 1) | (reviews_df['score'] > 5)]
        if not review_score_outliers.empty:
            anomalies.append(f"Reviews with invalid scores: {len(review_score_outliers)} records")
            print(f"{len(review_score_outliers)} reviews have invalid scores (outside 1-5 range)")
        else:
            print("All review scores are within valid range (1-5)")

    if 'thumbsUpCount' in reviews_df.columns:
        negative_thumbs = reviews_df[reviews_df['thumbsUpCount'] < 0]
        if not negative_thumbs.empty:
            anomalies.append(f"Reviews with negative thumbs: {len(negative_thumbs)} records")
            print(f"{len(negative_thumbs)} reviews have negative thumbs-up counts")
        else:
            print("All thumbs-up counts are non-negative")

    apps_missing_critical = apps_df[
        (apps_df['appId'] == '') | (apps_df['title'] == '') | (apps_df['appId'].isna())
    ]
    if not apps_missing_critical.empty:
        anomalies.append(f"Apps with missing critical info: {len(apps_missing_critical)} records")
        print(f"{len(apps_missing_critical)} apps have missing critical information")
    else:
        print("All apps have critical information")

    reviews_missing_critical = reviews_df[
        (reviews_df['app_id'] == '') | (reviews_df['reviewId'] == '') | (reviews_df['app_id'].isna())
    ]
    if not reviews_missing_critical.empty:
        anomalies.append(f"Reviews with missing critical info: {len(reviews_missing_critical)} records")
        print(f"{len(reviews_missing_critical)} reviews have missing critical information")
    else:
        print("All reviews have critical information")

    if not anomalies:
        print("No obvious anomalies detected!")
    else:
        print(f"Anomalies documented: {anomalies}")

def run_comprehensive_verification():
    print("Starting comprehensive verification of transformed datasets...\n")

    try:
        apps_df, reviews_df = load_processed_data()

        verify_tabular_consistency(apps_df, reviews_df)
        verify_join_capability(apps_df, reviews_df)
        verify_numeric_fields(apps_df, reviews_df)
        verify_timestamp_aggregation(reviews_df)
        identify_anomalies(apps_df, reviews_df)

        print(f"SUMMARY")
        print(f"Apps dataset: {apps_df.shape[0]} rows, {apps_df.shape[1]} columns")
        print(f"Reviews dataset: {reviews_df.shape[0]} rows, {reviews_df.shape[1]} columns")
        print("Verification complete!")

    except FileNotFoundError:
        print("Error: Processed datasets not found. Please run transformer.py first.")
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    run_comprehensive_verification()