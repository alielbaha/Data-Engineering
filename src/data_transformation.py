import json
import pandas as pd
from datetime import datetime
import numpy as np
import os
import re

def inspect_raw_data(file_path):
    if file_path.endswith('.csv'):
        raw_data = pd.read_csv(file_path)
        raw_data_list = raw_data.to_dict('records')
        print("RAW DATA INSPECTION (CSV)")
        print(f"Total entries: {len(raw_data_list)}")
        print(f"Data type: {type(raw_data_list)}")

        if raw_data_list and len(raw_data_list) > 0:
            sample_entry = raw_data_list[0]
            print(f"\nSample entry keys: {list(sample_entry.keys())}")

            for key, value in sample_entry.items():
                if isinstance(value, (dict, list)):
                    print(f"Field '{key}': {type(value)} with {len(value) if hasattr(value, '__len__') else 'unknown'} items")
                else:
                    print(f"Field '{key}': type={type(value)}, sample_value={str(value)[:100]}...")

        return raw_data_list
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        print("RAW DATA INSPECTION (JSON)")
        print(f"Total entries: {len(raw_data)}")
        print(f"Data type: {type(raw_data)}")

        if isinstance(raw_data, list) and len(raw_data) > 0:
            sample_entry = raw_data[0]
            print(f"\nSample entry keys: {list(sample_entry.keys())}")

            for key, value in sample_entry.items():
                if isinstance(value, (dict, list)):
                    print(f"Field '{key}': {type(value)} with {len(value) if hasattr(value, '__len__') else 'unknown'} items")
                else:
                    print(f"Field '{key}': type={type(value)}, sample_value={str(value)[:100]}...")

        return raw_data


issues = [
    "reviews are embedded within each app object instead of separate table",
    "descriptions contain HTML tags and special characters",
    "number of installs field stored as text (1,000,000+) instead of numeric",
    "data contains images",
    "free apps have price=0 but mixed with currency field",
    "Descriptions contain HTML parts and special characters",
    "extra fields"
]



def clean_installs(installs_str):
    
    if pd.isna(installs_str) or installs_str == '':
        return 0
    

    clean_str = str(installs_str).replace('+', '').replace(',', '')

    match = re.search(r'(\d+)', clean_str)
    return int(match.group(1)) if match else 0

#html cleannig
def clean_description(desc):
    
    if pd.isna(desc):
        return ""
    
    desc = str(desc).replace('\r\n', ' ').replace('<br>', ' ').replace('<br/>', ' ')
   
    desc = ' '.join(desc.split())
    return desc

def clean_and_transform_data(raw_data):  

    apps_list = []
    reviews_list = []

    if raw_data and isinstance(raw_data[0], dict) and 'app_id' in raw_data[0]:
        
        for entry in raw_data:
            review_info = {
                'app_id': entry.get('app_id', ''),
                'app_name': entry.get('app_name', ''),
                'reviewId': entry.get('reviewId', ''),
                'userName': entry.get('userName', ''),
                'score': int(entry.get('score')) if entry.get('score') is not None else 0,
                'content': entry.get('content', ''),
                'thumbsUpCount': int(entry.get('thumbsUpCount')) if entry.get('thumbsUpCount') is not None else 0,
                'at': pd.to_datetime(entry.get('at'), errors='coerce')  # Convert to datetime
            }
            reviews_list.append(review_info)
        
        
        unique_apps = {}
        for review in reviews_list:
            app_id = review['app_id']
            if app_id not in unique_apps:
                unique_apps[app_id] = {
                    'appId': app_id,
                    'title': review['app_name'],
                    'developer': 'Unknown',  
                    'score': 0.0, 
                    'ratings': 0,   
                    'installs': 0, 
                    'genre': 'Unknown',  
                    'price': 0.0    
                }
        

        app_scores = {}
        app_counts = {}
        for review in reviews_list:
            app_id = review['app_id']
            if app_id not in app_scores:
                app_scores[app_id] = []
            app_scores[app_id].append(review['score'])
            if app_id not in app_counts:
                app_counts[app_id] = 0
            app_counts[app_id] += 1
        
        for app_id in unique_apps:
            if app_scores[app_id]:
                unique_apps[app_id]['score'] = sum(app_scores[app_id]) / len(app_scores[app_id])
            unique_apps[app_id]['ratings'] = app_counts[app_id]
        
        apps_list = list(unique_apps.values())
    else:
        
        for entry in raw_data:
            app_info = {
                'appId': entry.get('appId', ''),
                'title': entry.get('title', ''),
                'developer': entry.get('developer', ''),
                'score': float(entry.get('score')) if entry.get('score') is not None else 0.0,
                'ratings': int(entry.get('ratings')) if entry.get('ratings') is not None else 0,
                'installs': clean_installs(entry.get('installs', '')),
                'genre': entry.get('genre', ''),
                'price': float(entry.get('price')) if entry.get('price') is not None else 0.0
            }

            apps_list.append(app_info)

            reviews = entry.get('reviews', [])
            if reviews and isinstance(reviews, list):
                for review in reviews:
                    if isinstance(review, dict):
                        review_info = {
                            'app_id': entry.get('appId', ''),
                            'app_name': entry.get('title', ''),
                            'reviewId': review.get('reviewId', ''),
                            'userName': review.get('userName', ''),
                            'score': int(review.get('score')) if review.get('score') is not None else 0,
                            'content': review.get('content', ''),
                            'thumbsUpCount': int(review.get('thumbsUpCount')) if review.get('thumbsUpCount') is not None else 0,
                            'at': pd.to_datetime(review.get('at'), errors='coerce')  # Convert to datetime
                        }
                        reviews_list.append(review_info)

    apps_df = pd.DataFrame(apps_list)
    reviews_df = pd.DataFrame(reviews_list)

    return apps_df, reviews_df

def clean_dataframe_types(df, df_type='apps'): 
   
    if df_type == 'apps':
        
        df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0.0)
        df['ratings'] = pd.to_numeric(df['ratings'], errors='coerce').fillna(0)
        df['installs'] = pd.to_numeric(df['installs'], errors='coerce').fillna(0)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)
        
    elif df_type == 'reviews':
    
        df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
        df['thumbsUpCount'] = pd.to_numeric(df['thumbsUpCount'], errors='coerce').fillna(0)
        
        # timestamp -> datetime
        df['at'] = pd.to_datetime(df['at'], errors='coerce')
    
    return df

def main():
    print("Starting full refresh of data transformation pipeline...")

    raw_file = '../data/raw/note_taking_ai_reviews_batch2.csv'
    processed_dir = '../data/processed/'

    os.makedirs(processed_dir, exist_ok=True)

    raw_data = inspect_raw_data(raw_file)
    
    print(f"Processing {len(raw_data)} raw records...")

    apps_df, reviews_df = clean_and_transform_data(raw_data)
    
    print(f"Original reviews count: {len(reviews_df)}")
    initial_reviews_count = len(reviews_df)
    reviews_df = reviews_df.sort_values('at').drop_duplicates(subset=['reviewId'], keep='last')
    final_reviews_count = len(reviews_df)
    print(f"After deduplication: {final_reviews_count} reviews (removed {initial_reviews_count - final_reviews_count} duplicates)")
    
    unique_apps_in_reviews = set(reviews_df['app_id'].unique())
    apps_in_catalog = set(apps_df['appId'].unique())
    print(f"Apps in reviews: {len(unique_apps_in_reviews)}, Apps in catalog: {len(apps_in_catalog)}")
    
    missing_apps = unique_apps_in_reviews - apps_in_catalog
    if missing_apps:
        print(f"Warning: {len(missing_apps)} apps referenced in reviews are not in apps catalog")
    
 
    apps_df = clean_dataframe_types(apps_df, 'apps')
    reviews_df = clean_dataframe_types(reviews_df, 'reviews')
    
   
    apps_output_path = os.path.join(processed_dir, 'apps_catalog.csv')
    reviews_output_path = os.path.join(processed_dir, 'apps_reviews.csv')
    
    apps_df.to_csv(apps_output_path, index=False)
    reviews_df.to_csv(reviews_output_path, index=False)
    
    print(f"")
    print(f"Apps catalog saved to: {apps_output_path}")
    print(f"Reviews data saved to: {reviews_output_path}")
    print(f"Apps shape: {apps_df.shape}")
    print(f"Reviews shape: {reviews_df.shape}")
    

if __name__ == "__main__":
    main()
