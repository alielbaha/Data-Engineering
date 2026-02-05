from google_play_scraper import app, search, reviews
import json
import time
from datetime import datetime

def make_serializable(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: make_serializable(value) for key, value in obj.items()}
    else:
        return obj

keywords = ["AI notes", "take notes AI", "Notes AI", "AI notebook", "Smart notes"]

all_results = []

for keyword in keywords:
    print(f"Searching for: {keyword}")
    result = search(
        keyword,
        lang="en",  
        country="us", 
        n_hits=30  # max
    )
    
    for app_result in result:
        app_result['search_keyword'] = keyword
    
    all_results.extend(result)
    print(f"Found {len(result)} apps for '{keyword}'")

# removed dupplicates
unique_apps = []
seen_app_ids = set()

for app_result in all_results:
    app_id = app_result.get('appId')
    if app_id and app_id not in seen_app_ids:
        unique_apps.append(app_result)
        seen_app_ids.add(app_id)

print(f"Total unique apps collected: {len(unique_apps)}")

all_apps_with_reviews = []

for i, app_data in enumerate(unique_apps):
    app_id = app_data['appId']
    print(f"Extracting reviews for app {i+1}/{len(unique_apps)}: {app_data.get('title', app_id)}")
    
    try:
        app_reviews, continuation_token = reviews(
            app_id,
            lang='en',
            country='us',
            count=100 
        )
        
        # datetime -> strings
        serializable_reviews = make_serializable(app_reviews)
        app_data['reviews'] = serializable_reviews
        print(f"  -> Retrieved {len(serializable_reviews)} reviews")
        
    except Exception as e:
        print(f"  -> Error fetching reviews: {str(e)}")
        app_data['reviews'] = []
    
    time.sleep(1)
    
    all_apps_with_reviews.append(app_data)

final_data = make_serializable(all_apps_with_reviews)

with open('data/raw/ai_note_apps_with_reviews.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)


print(f"Resultat 'data/raw/ai_note_apps_with_reviews.json'")
