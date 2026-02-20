from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


def shorten(label: str, max_len: int = 32) -> str:
    if label is None:
        return "Unknown"
    label = str(label).strip()
    return label if len(label) <= max_len else label[: max_len - 3] + "..."


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    db_path = root / "dbt" / "data" / "duckdb" / "playstore.duckdb"
    out_dir = root / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(db_path), read_only=True)

    # A) Monthly trend from staging reviews (stable even if downstream fact changes)
    monthly_rows = con.sql(
        """
        select
            strftime(cast(review_timestamp as date), '%Y-%m') as year_month,
            round(avg(rating_score), 4) as avg_rating,
            count(*) as review_count
        from stg_playstore_reviews
        where review_timestamp is not null
        group by 1
        order by 1
        """
    ).fetchall()

    # B) App-level metrics for popularity vs satisfaction scatter
    app_perf_rows = con.sql(
        """
        select
            app_name,
            count(*) as number_of_reviews,
            round(avg(rating_score), 4) as average_rating,
            round(100.0 * sum(case when rating_score <= 2 then 1 else 0 end) / nullif(count(*), 0), 2) as low_rating_pct
        from stg_playstore_reviews
        where app_name is not null
        group by 1
        having count(*) >= 20
        order by number_of_reviews desc
        """
    ).fetchall()

    # C) Worst apps by % low ratings
    worst_rows = con.sql(
        """
        select
            app_name,
            round(100.0 * sum(case when rating_score <= 2 then 1 else 0 end) / nullif(count(*), 0), 2) as low_rating_pct,
            count(*) as review_count
        from stg_playstore_reviews
        where app_name is not null
        group by 1
        having count(*) >= 20
        order by low_rating_pct desc, review_count desc
        limit 10
        """
    ).fetchall()

    plt.style.use("seaborn-v0_8-whitegrid")

    # 1) Monthly Average Rating Trend
    months = [r[0] for r in monthly_rows]
    avg_ratings = [float(r[1]) for r in monthly_rows]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(months, avg_ratings, marker="o", linewidth=2.5, color="#1f77b4")
    ax.set_title("Monthly Average Rating Trend", fontsize=16, pad=12)
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Average Rating", fontsize=11)
    ax.set_ylim(0, 5)

    # Keep only a subset of ticks to avoid clutter
    n = len(months)
    step = max(1, n // 12)
    tick_idx = list(range(0, n, step))
    if (n - 1) not in tick_idx:
        tick_idx.append(n - 1)
    ax.set_xticks(tick_idx)
    ax.set_xticklabels([months[i] for i in tick_idx], rotation=35, ha="right")

    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "rating_trend.png", dpi=170)
    plt.close(fig)

    # 2) App Performance: Popularity vs Satisfaction (scatter)
    names = [r[0] for r in app_perf_rows]
    reviews = [int(r[1]) for r in app_perf_rows]
    ratings = [float(r[2]) for r in app_perf_rows]
    low_pct = [float(r[3]) for r in app_perf_rows]

    fig, ax = plt.subplots(figsize=(11, 7))
    sizes = [max(80, min(900, rv * 1.7)) for rv in reviews]
    sc = ax.scatter(
        reviews,
        ratings,
        c=low_pct,
        s=sizes,
        cmap=plt.colormaps["RdYlGn_r"],
        alpha=0.82,
        edgecolors="white",
        linewidths=0.9,
    )

    ax.set_title("App Performance: Popularity vs Satisfaction", fontsize=16, pad=12)
    ax.set_xlabel("Number of Reviews", fontsize=11)
    ax.set_ylabel("Average Rating", fontsize=11)
    ax.set_ylim(1, 5)
    ax.grid(alpha=0.2)

    cbar = fig.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("% Low Ratings (<= 2)", fontsize=10)

    # annotate a few most reviewed apps
    top_idx = sorted(range(len(reviews)), key=lambda i: reviews[i], reverse=True)[:6]
    for i in top_idx:
        ax.annotate(
            shorten(names[i], 18),
            (reviews[i], ratings[i]),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
            alpha=0.9,
        )

    fig.tight_layout()
    fig.savefig(out_dir / "app_performance.png", dpi=170)
    plt.close(fig)

    # 3) Apps with Highest Percentage of Low Ratings
    app_labels = [shorten(r[0], 34) for r in worst_rows]
    low_values = [float(r[1]) for r in worst_rows]

    fig, ax = plt.subplots(figsize=(11, 7))
    reds = plt.colormaps["Reds"]
    colors = reds([0.35 + 0.6 * (v / max(low_values)) if max(low_values) > 0 else 0.35 for v in low_values])
    ax.barh(app_labels[::-1], low_values[::-1], color=colors[::-1], edgecolor="none")

    ax.set_title("Apps with Highest Percentage of Low Ratings", fontsize=16, pad=12)
    ax.set_xlabel("% Low Ratings (<= 2)", fontsize=11)
    ax.set_ylabel("Application", fontsize=11)
    ax.set_xlim(0, max(10, max(low_values) * 1.12 if low_values else 10))
    ax.grid(axis="x", alpha=0.25)

    for idx, val in enumerate(low_values[::-1]):
        ax.text(val + 0.5, idx, f"{val:.1f}%", va="center", fontsize=8)

    fig.tight_layout()
    fig.savefig(out_dir / "worst_apps.png", dpi=170)
    plt.close(fig)

    print(f"created: {out_dir / 'rating_trend.png'}")
    print(f"created: {out_dir / 'app_performance.png'}")
    print(f"created: {out_dir / 'worst_apps.png'}")


if __name__ == "__main__":
    main()
