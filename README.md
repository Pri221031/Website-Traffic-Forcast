# Website Traffic Analysis & Forecasting

End-to-end analytics project that analyzes user behaviour, visualizes key
traffic KPIs, and forecasts future website traffic — built with **Python,
SQL, Excel/CSV, and Power BI**.

## Business Question
How is our website traffic trending, which acquisition channels perform
best, and what should we expect over the next 30 days?

## Dataset
`data/website_traffic.csv` — 731 days (2024–2025) of daily traffic data:
sessions, users, pageviews, average session duration, bounce rate,
conversions, channel, and device.

> This project ships with a realistic **synthetic** dataset
> (`data/generate_data.py`) so it's fully reproducible without an external
> download. Swap in a real Google Analytics (GA4) export and the same
> pipeline works unchanged — just match the column names.

## Tech Stack
| Layer | Tool |
|---|---|
| Data storage & querying | SQLite (SQL) |
| Cleaning & forecasting | Python (pandas, scikit-learn) |
| Visualization | Matplotlib (charts) + Power BI (interactive dashboard) |

## Project Structure
```
website-traffic-analysis/
├── data/
│   ├── generate_data.py                  # synthetic data generator
│   ├── website_traffic.csv               # raw dataset
│   ├── monthly_summary_for_powerbi.csv   # Power BI-ready summary
│   └── traffic_forecast_next_30_days.csv # forecast output
├── sql/
│   ├── 01_schema.sql                     # table schema
│   └── 02_analysis_queries.sql           # 7 business-question queries
├── notebooks/
│   └── eda_and_forecast.py               # EDA + forecasting script
├── charts/                               # generated PNG charts
└── traffic.db                            # SQLite database
```

## How to Run
```bash
# 1. Generate the dataset
python data/generate_data.py

# 2. Build the SQLite database and run the schema
sqlite3 traffic.db < sql/01_schema.sql
python -c "import sqlite3,pandas as pd; c=sqlite3.connect('traffic.db'); pd.read_csv('data/website_traffic.csv').to_sql('website_traffic', c, if_exists='append', index=False)"

# 3. Explore the SQL business questions
sqlite3 traffic.db < sql/02_analysis_queries.sql

# 4. Run the Python EDA + forecast
python notebooks/eda_and_forecast.py
```

## Key Findings
- **Traffic grew steadily** over the two-year window, with clear yearly
  seasonality (dip in mid-year, peak around Oct–Dec).
- **Weekdays outperform weekends**: ~1,758 avg sessions/day on weekdays vs
  ~1,162 on weekends — consistent with a B2B-style audience.
- **Organic Search is the top channel** by volume (~412K sessions), and all
  channels convert in a fairly tight 2.6–2.8% range, so the growth lever is
  *volume*, not channel-level conversion optimization.
- **30-day forecast**: a simple, explainable linear-trend + weekday model
  projects continued growth into the next month (see
  `data/traffic_forecast_next_30_days.csv`).

## Power BI Dashboard
Import `data/website_traffic.csv` (raw, for interactivity) and
`data/monthly_summary_for_powerbi.csv` (for a fast monthly-KPI view) into
Power BI. Suggested visuals:
1. Line chart: sessions over time with a 7-day rolling average
2. Bar chart: sessions & conversion rate by channel
3. KPI cards: total sessions, total conversions, avg bounce rate
4. Donut chart: device split (Desktop / Mobile / Tablet)
5. Slicer: date range + channel

## Author
Priyanka Kumari — [LinkedIn](https://linkedin.com/in/your-profile) · [GitHub](https://github.com/your-username)
