import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
from flask import Flask, render_template_string
import io
import base64

def load_serving_data():
    """Load the serving layer datasets"""
    processed_dir = '../data/processed/'
    
    app_kpis = pd.read_csv(os.path.join(processed_dir, 'app_level_kpis.csv'))
    daily_metrics = pd.read_csv(os.path.join(processed_dir, 'daily_metrics.csv'))
    
    # Convert date columns
    app_kpis['first_review_date'] = pd.to_datetime(app_kpis['first_review_date'])
    app_kpis['most_recent_review_date'] = pd.to_datetime(app_kpis['most_recent_review_date'])
    daily_metrics['date'] = pd.to_datetime(daily_metrics['date'])
    
    return app_kpis, daily_metrics

def plot_app_performance(app_kpis):
    """Generate app performance plots and return as base64 string"""
    # 1. Top performing apps by average rating (with sufficient reviews)
    app_kpis_filtered = app_kpis[app_kpis['number_of_reviews'] >= 10]  # Filter for apps with enough reviews
    top_apps = app_kpis_filtered.nlargest(10, 'average_rating')

    plt.figure(figsize=(12, 8))
    plt.subplot(2, 2, 1)
    plt.barh(range(len(top_apps)), top_apps['average_rating'], color='green', alpha=0.7)
    plt.yticks(range(len(top_apps)), [f"{title[:20]}..." if len(title) > 20 else title for title in top_apps['app_id']])
    plt.xlabel('Average Rating')
    plt.title('Top 10 Apps by Average Rating (≥10 reviews)')
    plt.xlim(0, 5)
    plt.grid(axis='x', linestyle='--', alpha=0.6)

    # 2. Low rating percentage analysis
    bottom_apps = app_kpis.nlargest(10, '%_low_rating_reviews')
    plt.subplot(2, 2, 2)
    plt.barh(range(len(bottom_apps)), bottom_apps['%_low_rating_reviews'], color='red', alpha=0.7)
    plt.yticks(range(len(bottom_apps)), [f"{title[:20]}..." if len(title) > 20 else title for title in bottom_apps['app_id']])
    plt.xlabel('% Low Rating Reviews')
    plt.title('Top 10 Apps by % Low Rating Reviews')
    plt.grid(axis='x', linestyle='--', alpha=0.6)

    # 3. Review volume comparison
    top_volume = app_kpis.nlargest(10, 'number_of_reviews')
    plt.subplot(2, 2, 3)
    plt.barh(range(len(top_volume)), top_volume['number_of_reviews'], color='blue', alpha=0.7)
    plt.yticks(range(len(top_volume)), [f"{title[:20]}..." if len(title) > 20 else title for title in top_volume['app_id']])
    plt.xlabel('Number of Reviews')
    plt.title('Top 10 Apps by Review Volume')
    plt.grid(axis='x', linestyle='--', alpha=0.6)

    # 4. Correlation between reviews and ratings
    plt.subplot(2, 2, 4)
    plt.scatter(app_kpis['number_of_reviews'], app_kpis['average_rating'], alpha=0.6, s=50)
    plt.xlabel('Number of Reviews')
    plt.ylabel('Average Rating')
    plt.title('Review Volume vs Average Rating')
    plt.grid(linestyle='--', alpha=0.6)

    # Add trend line
    z = np.polyfit(app_kpis['number_of_reviews'], app_kpis['average_rating'], 1)
    p = np.poly1d(z)
    plt.plot(app_kpis['number_of_reviews'], p(app_kpis['number_of_reviews']), "r--", alpha=0.8)

    plt.suptitle('App Performance Dashboard', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Convert plot to base64 string
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()  # Close the figure to free memory
    
    return plot_url

def plot_time_trends(daily_metrics):
    """Generate time trends plots and return as base64 string"""
    # Sort by date for proper plotting
    daily_metrics_sorted = daily_metrics.sort_values('date')

    plt.figure(figsize=(14, 10))
    
    # 1. Daily number of reviews over time
    plt.subplot(2, 1, 1)
    plt.plot(daily_metrics_sorted['date'], daily_metrics_sorted['daily_number_of_reviews'],
             marker='o', linewidth=2, markersize=4, alpha=0.7)
    plt.xlabel('Date')
    plt.ylabel('Daily Number of Reviews')
    plt.title('Daily Review Volume Over Time')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tick_params(axis='x', rotation=45)

    # 2. Daily average rating over time
    plt.subplot(2, 1, 2)
    plt.plot(daily_metrics_sorted['date'], daily_metrics_sorted['daily_average_rating'],
             color='orange', marker='o', linewidth=2, markersize=4, alpha=0.7)
    plt.xlabel('Date')
    plt.ylabel('Daily Average Rating')
    plt.title('Daily Average Rating Over Time')
    plt.ylim(0, 5.5)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tick_params(axis='x', rotation=45)

    plt.suptitle('Time-Based Trends Dashboard', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Convert plot to base64 string
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()  # Close the figure to free memory
    
    return plot_url

def print_key_insights(app_kpis, daily_metrics):
    """Print key insights from the data"""
    print("=== KEY INSIGHTS FROM THE DASHBOARD ===\n")
    
    # Best and worst performing apps
    best_app = app_kpis.loc[app_kpis['average_rating'].idxmax()]
    worst_app = app_kpis.loc[app_kpis['average_rating'].idxmin()]
    
    print(f"🏆 BEST PERFORMING APP:")
    print(f"   App ID: {best_app['app_id']}")
    print(f"   Average Rating: {best_app['average_rating']:.2f}")
    print(f"   Number of Reviews: {best_app['number_of_reviews']}")
    print(f"   % Low Ratings: {best_app['%_low_rating_reviews']:.2f}%\n")
    
    print(f"📉 WORST PERFORMING APP:")
    print(f"   App ID: {worst_app['app_id']}")
    print(f"   Average Rating: {worst_app['average_rating']:.2f}")
    print(f"   Number of Reviews: {worst_app['number_of_reviews']}")
    print(f"   % Low Ratings: {worst_app['%_low_rating_reviews']:.2f}%\n")
    
    # Review volume insights
    top_volume_app = app_kpis.loc[app_kpis['number_of_reviews'].idxmax()]
    print(f"📊 HIGHEST REVIEW VOLUME APP:")
    print(f"   App ID: {top_volume_app['app_id']}")
    print(f"   Number of Reviews: {top_volume_app['number_of_reviews']}")
    print(f"   Average Rating: {top_volume_app['average_rating']:.2f}\n")
    
    # Time trend insights
    daily_metrics_sorted = daily_metrics.sort_values('date')
    if len(daily_metrics_sorted) >= 2:
        avg_rating_start = daily_metrics_sorted.iloc[0]['daily_average_rating']
        avg_rating_end = daily_metrics_sorted.iloc[-1]['daily_average_rating']
        rating_change = avg_rating_end - avg_rating_start
        
        print(f"📈 TIME TREND INSIGHTS:")
        print(f"   Average rating change over time: {rating_change:+.2f}")
        print(f"   Overall rating trend: {'Improving' if rating_change > 0 else 'Declining'}")
        print(f"   Total review days in dataset: {len(daily_metrics_sorted)}")
        print(f"   Date range: {daily_metrics_sorted.iloc[0]['date'].strftime('%Y-%m-%d')} to {daily_metrics_sorted.iloc[-1]['date'].strftime('%Y-%m-%d')}\n")

def create_dashboard():
    """Create and serve the dashboard via Flask"""
    print("Loading serving layer datasets for dashboard...\n")

    try:
        # Load serving layer data
        app_kpis, daily_metrics = load_serving_data()

        print(f"Loaded {len(app_kpis)} apps and {len(daily_metrics)} daily records")

        # Generate plots
        print("Generating app performance dashboard...")
        app_plot_url = plot_app_performance(app_kpis)

        print("Generating time trend dashboard...")
        time_plot_url = plot_time_trends(daily_metrics)

        # Create Flask app
        app = Flask(__name__)

        @app.route('/')
        def dashboard():
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            insights_html = generate_insights_html(app_kpis, daily_metrics)
            return render_template_string(HTML_TEMPLATE, 
                                         app_plot_url=app_plot_url, 
                                         time_plot_url=time_plot_url,
                                         insights_html=insights_html,
                                         current_time=current_time)

        print("Starting dashboard server...")
        print("Open your browser and go to http://127.0.0.1:5000/")
        app.run(debug=True, use_reloader=False)  # use_reloader=False to prevent issues with plots

    except FileNotFoundError:
        print("Error: Serving layer datasets not found. Please run the aggregation step first.")
    except Exception as e:
        print(f"Error creating dashboard: {e}")


def generate_insights_html(app_kpis, daily_metrics):
    """Generate HTML for key insights"""
    # Best and worst performing apps
    best_app = app_kpis.loc[app_kpis['average_rating'].idxmax()]
    worst_app = app_kpis.loc[app_kpis['average_rating'].idxmin()]
    
    # Review volume insights
    top_volume_app = app_kpis.loc[app_kpis['number_of_reviews'].idxmax()]
    
    # Time trend insights
    daily_metrics_sorted = daily_metrics.sort_values('date')
    avg_rating_start = daily_metrics_sorted.iloc[0]['daily_average_rating']
    avg_rating_end = daily_metrics_sorted.iloc[-1]['daily_average_rating']
    rating_change = avg_rating_end - avg_rating_start

    html = f"""
    <div class="insights">
        <h2>Key Insights</h2>
        <div class="insight-card">
            <h3>🏆 Best Performing App:</h3>
            <p><strong>App ID:</strong> {best_app['app_id']}</p>
            <p><strong>Average Rating:</strong> {best_app['average_rating']:.2f}</p>
            <p><strong>Number of Reviews:</strong> {best_app['number_of_reviews']}</p>
            <p><strong>% Low Ratings:</strong> {best_app['%_low_rating_reviews']:.2f}%</p>
        </div>
        
        <div class="insight-card">
            <h3>📉 Worst Performing App:</h3>
            <p><strong>App ID:</strong> {worst_app['app_id']}</p>
            <p><strong>Average Rating:</strong> {worst_app['average_rating']:.2f}</p>
            <p><strong>Number of Reviews:</strong> {worst_app['number_of_reviews']}</p>
            <p><strong>% Low Ratings:</strong> {worst_app['%_low_rating_reviews']:.2f}%</p>
        </div>
        
        <div class="insight-card">
            <h3>📊 Highest Review Volume App:</h3>
            <p><strong>App ID:</strong> {top_volume_app['app_id']}</p>
            <p><strong>Number of Reviews:</strong> {top_volume_app['number_of_reviews']}</p>
            <p><strong>Average Rating:</strong> {top_volume_app['average_rating']:.2f}</p>
        </div>
        
        <div class="insight-card">
            <h3>📈 Time Trend Insights:</h3>
            <p><strong>Average rating change over time:</strong> {rating_change:+.2f}</p>
            <p><strong>Overall rating trend:</strong> {'Improving' if rating_change > 0 else 'Declining'}</p>
            <p><strong>Total review days in dataset:</strong> {len(daily_metrics_sorted)}</p>
            <p><strong>Date range:</strong> {daily_metrics_sorted.iloc[0]['date'].strftime('%Y-%m-%d')} to {daily_metrics_sorted.iloc[-1]['date'].strftime('%Y-%m-%d')}</p>
        </div>
    </div>
    """
    return html


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Notes App Analytics Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .dashboard-section {
            margin-bottom: 40px;
        }
        .dashboard-section h2 {
            color: #444;
            border-bottom: 2px solid #ddd;
            padding-bottom: 10px;
        }
        .plot-container {
            text-align: center;
            margin: 20px 0;
        }
        .plot-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .insights {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .insight-card {
            background-color: white;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .insight-card h3 {
            margin-top: 0;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Notes App Analytics Dashboard</h1>
        
        <div class="dashboard-section">
            <h2>App Performance Metrics</h2>
            <div class="plot-container">
                <img src="data:image/png;base64,{{ app_plot_url }}" alt="App Performance Dashboard">
            </div>
        </div>
        
        <div class="dashboard-section">
            <h2>Time-Based Trends</h2>
            <div class="plot-container">
                <img src="data:image/png;base64,{{ time_plot_url }}" alt="Time-Based Trends Dashboard">
            </div>
        </div>
        
        {{ insights_html|safe }}
        
        <footer>
            <p style="text-align: center; margin-top: 30px; color: #777;">
                AI Notes App Analytics Dashboard | Generated on {{ current_time }}
            </p>
        </footer>
    </div>
</body>
</html>
'''


if __name__ == "__main__":
    create_dashboard()