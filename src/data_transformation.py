import json
import pandas as pd
from datetime import datetime
import numpy as np
import os
import re

def inspect_raw_data(file_path):
  
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    print("=== RAW DATA INSPECTION ===")
    print(f"Total entries: {len(raw_data)}")
    print(f"Data type: {type(raw_data)}")
    
    # Sample first entry to understand structure
    if isinstance(raw_data, list) and len(raw_data) > 0:
        sample_entry = raw_data[0]
        print(f"\nSample entry keys: {list(sample_entry.keys())}")
        
        # Check for nested structures
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



#Convert installs string to numeric value
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

def clean_and_transform_data(raw_data):  #raw JSON -> df
    
    apps_list = []
    reviews_list = []
    
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
                        'at': review.get('at', '')
                    }
                    reviews_list.append(review_info)
    
    apps_df = pd.DataFrame(apps_list)
    reviews_df = pd.DataFrame(reviews_list)
    
    return apps_df, reviews_df

def clean_dataframe_types(df, df_type='apps'): 
#standardizing data types
   
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

    raw_file = '../data/raw/ai_note_apps_with_reviews.json'
    processed_dir = '../data/processed/'
    
    os.makedirs(processed_dir, exist_ok=True)
    
    raw_data = inspect_raw_data(raw_file)
    

    apps_df, reviews_df = clean_and_transform_data(raw_data)
    
 
    apps_df = clean_dataframe_types(apps_df, 'apps')
    reviews_df = clean_dataframe_types(reviews_df, 'reviews')
    
   
    apps_output_path = os.path.join(processed_dir, 'apps_catalog.csv')
    reviews_output_path = os.path.join(processed_dir, 'apps_reviews.csv')
    
    apps_df.to_csv(apps_output_path, index=False)
    reviews_df.to_csv(reviews_output_path, index=False)
    
    print(f"\n=== TRANSFORMATION COMPLETE ===")
    print(f"Apps catalog saved to: {apps_output_path}")
    print(f"Reviews data saved to: {reviews_output_path}")
    print(f"Apps shape: {apps_df.shape}")
    print(f"Reviews shape: {reviews_df.shape}")
    
    # Display sample of cleaned data
    print(f"\n=== SAMPLE OF PROCESSED APPS DATA ===")
    print(apps_df.head(100))
    
    print(f"\n=== SAMPLE OF PROCESSED REVIEWS DATA ===")  
    print(reviews_df.head())

if __name__ == "__main__":
    main()