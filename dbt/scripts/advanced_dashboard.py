from pathlib import Path
import duckdb
from flask import Flask, jsonify, request, render_template_string


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "dbt" / "data" / "duckdb" / "playstore.duckdb"

app = Flask(__name__)


def fetch_dashboard_data(min_reviews: int, top_n: int):
    con = duckdb.connect(str(DB_PATH), read_only=True)

    kpi = con.sql(
        """
        select
            (select count(*) from stg_playstore_apps) as total_apps,
            (select count(*) from stg_playstore_reviews) as total_reviews,
            (select round(avg(rating_score), 2) from stg_playstore_reviews) as avg_rating,
            (select min(cast(review_timestamp as date)) from stg_playstore_reviews) as min_date,
            (select max(cast(review_timestamp as date)) from stg_playstore_reviews) as max_date
        """
    ).fetchone()

    app_metrics = con.sql(
        f"""
        select
            app_id,
            coalesce(nullif(trim(app_name), ''), app_id) as app_name,
            count(*) as review_count,
            round(avg(rating_score), 3) as avg_rating,
            round(100.0 * sum(case when rating_score <= 2 then 1 else 0 end) / nullif(count(*),0), 2) as low_pct
        from stg_playstore_reviews
        where app_id is not null
        group by 1, 2
        having count(*) >= {int(min_reviews)}
        order by review_count desc
        """
    ).fetchall()

    top_apps = sorted(app_metrics, key=lambda x: (x[2], x[1]), reverse=True)[:top_n]
    worst_apps = sorted(app_metrics, key=lambda x: (x[3], -x[1]), reverse=True)[:top_n]

    monthly = con.sql(
        """
        select
            strftime(cast(review_timestamp as date), '%Y-%m') as ym,
            round(avg(rating_score), 3) as avg_rating,
            count(*) as review_count
        from stg_playstore_reviews
        where review_timestamp is not null
        group by 1
        order by 1
        """
    ).fetchall()

    return {
        "kpis": {
            "total_apps": int(kpi[0]) if kpi[0] is not None else 0,
            "total_reviews": int(kpi[1]) if kpi[1] is not None else 0,
            "avg_rating": float(kpi[2]) if kpi[2] is not None else 0.0,
            "date_min": str(kpi[3]) if kpi[3] is not None else "n/a",
            "date_max": str(kpi[4]) if kpi[4] is not None else "n/a",
        },
        "top_apps": [
            {
                "app_id": r[0],
                "app_name": r[1],
                "review_count": int(r[2]),
                "avg_rating": float(r[3]),
                "low_pct": float(r[4]),
            }
            for r in top_apps
        ],
        "worst_apps": [
            {
                "app_id": r[0],
                "app_name": r[1],
                "review_count": int(r[2]),
                "avg_rating": float(r[3]),
                "low_pct": float(r[4]),
            }
            for r in worst_apps
        ],
        "scatter_apps": [
            {
                "app_id": r[0],
                "app_name": r[1],
                "review_count": int(r[2]),
                "avg_rating": float(r[3]),
                "low_pct": float(r[4]),
            }
            for r in app_metrics[:60]
        ],
        "monthly": [
            {"month": r[0], "avg_rating": float(r[1]), "review_count": int(r[2])}
            for r in monthly
        ],
        "meta": {
            "min_reviews": int(min_reviews),
            "top_n": int(top_n),
            "source": str(DB_PATH),
        },
    }


@app.get("/api/dashboard")
def api_dashboard():
    min_reviews = int(request.args.get("min_reviews", 20))
    top_n = int(request.args.get("top_n", 10))
    min_reviews = max(1, min(min_reviews, 500))
    top_n = max(3, min(top_n, 30))
    return jsonify(fetch_dashboard_data(min_reviews=min_reviews, top_n=top_n))


@app.get("/")
def home():
    return render_template_string(HTML)


HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PlayStore Intelligence Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #0f141a;
      --panel: #151d26;
      --card: #1b2733;
      --ink: #e8eef5;
      --muted: #9eb1c6;
      --line: #2a3b4d;
      --accent: #f2a65a;
      --accent2: #6ed3cf;
      --danger: #ef476f;
      --ok: #06d6a0;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(1200px 500px at -10% -10%, #203247 0%, rgba(15,20,26,0) 60%),
        radial-gradient(800px 400px at 110% 0%, #4d3323 0%, rgba(15,20,26,0) 60%),
        var(--bg);
    }
    .wrap { max-width: 1300px; margin: 0 auto; padding: 24px; }
    .header {
      display: flex; align-items: end; justify-content: space-between; gap: 16px;
      margin-bottom: 16px;
    }
    h1 { margin: 0; font-size: 34px; letter-spacing: .2px; }
    .sub { color: var(--muted); font-size: 14px; margin-top: 4px; }
    .controls {
      display: grid; grid-template-columns: repeat(2, minmax(160px, 1fr)); gap: 10px;
      background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 12px;
    }
    label { font-size: 12px; color: var(--muted); display: block; margin-bottom: 4px; }
    input, select {
      width: 100%; background: #0f1720; border: 1px solid var(--line); color: var(--ink);
      border-radius: 8px; padding: 8px 10px;
    }
    .kpis {
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 16px 0 18px;
    }
    .kpi {
      background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px;
    }
    .kpi .k { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .8px; }
    .kpi .v { font-size: 29px; margin-top: 8px; font-weight: 700; }

    .grid {
      display: grid;
      grid-template-columns: 1.1fr 1fr;
      gap: 12px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px;
      min-height: 340px;
    }
    .panel h3 { margin: 0 0 10px; font-size: 18px; }
    .panel canvas { width: 100% !important; height: 290px !important; }
    .wide { grid-column: span 2; }

    .table {
      width: 100%; border-collapse: collapse; font-size: 13px;
    }
    .table th, .table td { padding: 9px 8px; border-bottom: 1px solid var(--line); text-align: left; }
    .table th { color: var(--muted); font-weight: 600; }
    .badge { font-size: 11px; color: var(--muted); margin-top: 8px; }

    @media (max-width: 980px) {
      .kpis { grid-template-columns: repeat(2, 1fr); }
      .grid { grid-template-columns: 1fr; }
      .wide { grid-column: span 1; }
      .header { flex-direction: column; align-items: stretch; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <div>
        <h1>PlayStore Intelligence</h1>
        <div class="sub">Interactive analytics over DuckDB + dbt outputs/staging</div>
      </div>
      <div class="controls">
        <div>
          <label for="minReviews">Min Reviews per App</label>
          <input id="minReviews" type="number" min="1" max="500" value="20" />
        </div>
        <div>
          <label for="topN">Top N</label>
          <select id="topN">
            <option>8</option><option selected>10</option><option>12</option><option>15</option><option>20</option>
          </select>
        </div>
      </div>
    </div>

    <div class="kpis">
      <div class="kpi"><div class="k">Total Apps</div><div class="v" id="kApps">-</div></div>
      <div class="kpi"><div class="k">Total Reviews</div><div class="v" id="kReviews">-</div></div>
      <div class="kpi"><div class="k">Average Rating</div><div class="v" id="kAvg">-</div></div>
      <div class="kpi"><div class="k">Date Range</div><div class="v" id="kRange" style="font-size:18px">-</div></div>
    </div>

    <div class="grid">
      <section class="panel">
        <h3>Top Apps by Average Rating</h3>
        <canvas id="cTopApps"></canvas>
      </section>

      <section class="panel">
        <h3>Popularity vs Satisfaction</h3>
        <canvas id="cScatter"></canvas>
      </section>

      <section class="panel wide">
        <h3>Monthly Average Rating Trend</h3>
        <canvas id="cTrend"></canvas>
      </section>

      <section class="panel">
        <h3>Highest Low-Rating Pressure</h3>
        <canvas id="cWorst"></canvas>
      </section>

      <section class="panel">
        <h3>Risk Table (Worst Apps)</h3>
        <table class="table" id="riskTable">
          <thead><tr><th>App</th><th>Reviews</th><th>Avg Rating</th><th>% Low (<=2)</th></tr></thead>
          <tbody></tbody>
        </table>
        <div class="badge" id="meta"></div>
      </section>
    </div>
  </div>

<script>
let charts = {};

function shortLabel(s, n=28){ return s.length <= n ? s : s.slice(0, n-3) + '...'; }

async function loadData(){
  const minReviews = document.getElementById('minReviews').value || 20;
  const topN = document.getElementById('topN').value || 10;
  const url = `/api/dashboard?min_reviews=${minReviews}&top_n=${topN}`;
  const res = await fetch(url);
  const data = await res.json();
  render(data);
}

function destroyCharts(){
  Object.values(charts).forEach(c => c && c.destroy());
  charts = {};
}

function render(data){
  destroyCharts();

  document.getElementById('kApps').textContent = data.kpis.total_apps.toLocaleString();
  document.getElementById('kReviews').textContent = data.kpis.total_reviews.toLocaleString();
  document.getElementById('kAvg').textContent = Number(data.kpis.avg_rating).toFixed(2);
  document.getElementById('kRange').textContent = `${data.kpis.date_min} to ${data.kpis.date_max}`;
  document.getElementById('meta').textContent = `Filters -> min_reviews: ${data.meta.min_reviews}, top_n: ${data.meta.top_n}`;

  // Top Apps Bar
  const topApps = data.top_apps;
  charts.top = new Chart(document.getElementById('cTopApps'), {
    type: 'bar',
    data: {
      labels: topApps.map(x => shortLabel(x.app_name)),
      datasets: [{
        label: 'Average Rating',
        data: topApps.map(x => x.avg_rating),
        backgroundColor: '#6ed3cf'
      }]
    },
    options: {
      indexAxis: 'y',
      maintainAspectRatio: false,
      scales: { x: { min: 0, max: 5 } },
      plugins: { legend: { display: false } }
    }
  });

  // Scatter Bubble
  const sc = data.scatter_apps.map(x => ({
    x: x.review_count,
    y: x.avg_rating,
    r: Math.max(4, Math.min(18, Math.sqrt(x.review_count)/2)),
    low: x.low_pct,
    app: x.app_name
  }));
  charts.scatter = new Chart(document.getElementById('cScatter'), {
    type: 'bubble',
    data: {
      datasets: [{
        label: 'Apps',
        data: sc,
        backgroundColor: sc.map(p => p.low > 40 ? '#ef476f' : p.low > 25 ? '#f2a65a' : '#06d6a0')
      }]
    },
    options: {
      maintainAspectRatio: false,
      scales: {
        x: { title: { display: true, text: 'Number of Reviews'} },
        y: { min: 0, max: 5, title: { display: true, text: 'Average Rating'} }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const p = ctx.raw;
              return `${shortLabel(p.app, 40)} | rating=${p.y.toFixed(2)} | low%=${p.low.toFixed(1)} | reviews=${p.x}`;
            }
          }
        },
        legend: { display: false }
      }
    }
  });

  // Trend
  const tr = data.monthly;
  charts.trend = new Chart(document.getElementById('cTrend'), {
    type: 'line',
    data: {
      labels: tr.map(x => x.month),
      datasets: [{
        label: 'Average Rating',
        data: tr.map(x => x.avg_rating),
        borderColor: '#f2a65a',
        backgroundColor: 'rgba(242,166,90,.2)',
        tension: 0.25,
        pointRadius: 2.5
      }]
    },
    options: {
      maintainAspectRatio: false,
      scales: { y: { min: 0, max: 5 } },
      plugins: { legend: { display: false } }
    }
  });

  // Worst apps
  const worst = data.worst_apps;
  charts.worst = new Chart(document.getElementById('cWorst'), {
    type: 'bar',
    data: {
      labels: worst.map(x => shortLabel(x.app_name)),
      datasets: [{
        label: '% Low Ratings (<=2)',
        data: worst.map(x => x.low_pct),
        backgroundColor: '#ef476f'
      }]
    },
    options: {
      indexAxis: 'y',
      maintainAspectRatio: false,
      plugins: { legend: { display: false } }
    }
  });

  const tbody = document.querySelector('#riskTable tbody');
  tbody.innerHTML = '';
  worst.forEach(x => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${shortLabel(x.app_name, 38)}</td><td>${x.review_count}</td><td>${x.avg_rating.toFixed(2)}</td><td>${x.low_pct.toFixed(1)}%</td>`;
    tbody.appendChild(tr);
  });
}

document.getElementById('minReviews').addEventListener('change', loadData);
document.getElementById('topN').addEventListener('change', loadData);
loadData();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    print(f"Starting advanced dashboard on http://127.0.0.1:5050 (DB: {DB_PATH})")
    app.run(host="127.0.0.1", port=5050, debug=False)
