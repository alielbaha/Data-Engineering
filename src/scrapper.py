from google_play_scraper import app, search, reviews
import json
import time
from datetime import datetime
import os

def make_serializable(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: make_serializable(value) for key, value in obj.items()}
    else:
        return obj

def save_to_file(data, filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    
    existing_data.extend(data)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    return len(existing_data)

keywords = ["AI notes", "take notes AI", "Notes AI", "AI notebook", "Smart notes"]

all_results = []

for keyword in keywords:
    result = search(
        keyword,
        lang="en",  
        country="us", 
        n_hits=30  
    )
    
    for app_result in result:
        app_result['search_keyword'] = keyword
    
    all_results.extend(result)

unique_apps = []
seen_app_ids = set()

for app_result in all_results:
    app_id = app_result.get('appId')
    if app_id and app_id not in seen_app_ids:
        unique_apps.append(app_result)
        seen_app_ids.add(app_id)

output_file = 'data/raw/ai_note_apps_with_reviews.json'
os.makedirs(os.path.dirname(output_file), exist_ok=True)

processed_count = 0

for i, app_data in enumerate(unique_apps):
    app_id = app_data['appId']
    
    try:
        all_reviews = []
        continuation_token = None
        
        while len(all_reviews) < 100:
            remaining_count = 100 - len(all_reviews)
            count_to_fetch = min(100, remaining_count)
            
            if continuation_token is None:
                app_reviews, continuation_token = reviews(
                    app_id,
                    lang='en',
                    country='us',
                    count=count_to_fetch
                )
            else:
                app_reviews, continuation_token = reviews(
                    app_id,
                    lang='en',
                    country='us',
                    count=count_to_fetch,
                    continuation_token=continuation_token
                )
            
            all_reviews.extend(app_reviews)
            
            if not continuation_token:
                break
        
        serializable_reviews = make_serializable(all_reviews)
        app_data['reviews'] = serializable_reviews
        
    except Exception as e:
        app_data['reviews'] = []
    
    save_to_file([app_data], output_file)
    processed_count += 1
    
    time.sleep(1)

print(f"Résultats {output_file}")
