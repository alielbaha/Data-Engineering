import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_processed_data():
    """Load the processed reviews dataset"""
    processed_dir = '../data/processed/'
    reviews_df = pd.read_csv(os.path.join(processed_dir, 'apps_reviews.csv'))
    
    # Ensure timestamp column is datetime
    reviews_df['at'] = pd.to_datetime(reviews_df['at'], errors='coerce')
    
    # Remove rows with invalid timestamps
    reviews_df = reviews_df.dropna(subset=['at'])
    
    return reviews_df

def create_app_level_kpis(reviews_df):
    """Create app-level KPIs from reviews data"""
    print("Creating app-level KPIs...")
    
    app_kpis = reviews_df.groupby('app_id').agg({
        'reviewId': 'count',  # Number of reviews
        'score': 'mean',      # Average rating
        'at': ['min', 'max']  # First and most recent review dates
    }).round(4)
    
    # Flatten column names
    app_kpis.columns = ['number_of_reviews', 'average_rating', 'first_review_date', 'most_recent_review_date']
    
    # Calculate percentage of low rating reviews (≤ 2)
    low_rating_pct = reviews_df.groupby('app_id').apply(
        lambda x: (x['score'] <= 2).sum() / len(x) * 100
    ).round(2)
    
    # Combine with main dataframe
    app_kpis['percentage_low_ratings'] = low_rating_pct
    
    # Reset index to make app_id a regular column
    app_kpis = app_kpis.reset_index()
    
    # Rename columns to match requirements
    app_kpis = app_kpis.rename(columns={
        'number_of_reviews': 'number_of_reviews',
        'average_rating': 'average_rating',
        'percentage_low_ratings': '%_low_rating_reviews',
        'first_review_date': 'first_review_date',
        'most_recent_review_date': 'most_recent_review_date'
    })
    
    return app_kpis

def create_daily_metrics(reviews_df):
    """Create daily metrics from reviews data"""
    print("Creating daily metrics...")
    
    # Extract date from timestamp
    reviews_df['review_date'] = reviews_df['at'].dt.date
    
    # Group by date and calculate metrics
    daily_metrics = reviews_df.groupby('review_date').agg({
        'reviewId': 'count',  # Daily number of reviews
        'score': 'mean'       # Daily average rating
    }).round(4)
    
    # Rename columns
    daily_metrics.columns = ['daily_number_of_reviews', 'daily_average_rating']
    
    # Reset index to make date a regular column
    daily_metrics = daily_metrics.reset_index()
    daily_metrics = daily_metrics.rename(columns={'review_date': 'date'})
    
    return daily_metrics

def save_outputs(app_kpis, daily_metrics):
    """Save both output files to processed directory"""
    processed_dir = '../data/processed/'
    
    # Save app-level KPIs
    app_kpis_path = os.path.join(processed_dir, 'app_level_kpis.csv')
    app_kpis.to_csv(app_kpis_path, index=False)
    print(f"App-level KPIs saved to: {app_kpis_path}")
    
    # Save daily metrics
    daily_metrics_path = os.path.join(processed_dir, 'daily_metrics.csv')
    daily_metrics.to_csv(daily_metrics_path, index=False)
    print(f"Daily metrics saved to: {daily_metrics_path}")
    
    # Print summary statistics
    print(f"\n=== SUMMARY ===")
    print(f"App-level KPIs: {app_kpis.shape[0]} apps")
    print(f"Daily metrics: {daily_metrics.shape[0]} days")
    print(f"Date range: {daily_metrics['date'].min()} to {daily_metrics['date'].max()}")

def main():
    """Main function to orchestrate the aggregation process"""
    print("Starting aggregation of reviews data for serving layers...\n")
    
    # Load processed data
    reviews_df = load_processed_data()
    print(f"Loaded {reviews_df.shape[0]} reviews for aggregation")
    
    # Create app-level KPIs
    app_kpis = create_app_level_kpis(reviews_df)
    
    # Create daily metrics
    daily_metrics = create_daily_metrics(reviews_df)
    
    # Save outputs
    save_outputs(app_kpis, daily_metrics)
    
    print("\nAggregation complete! Serving layer datasets ready.")

if __name__ == "__main__":
    main()