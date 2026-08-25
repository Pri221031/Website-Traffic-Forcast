"""
eda_and_forecast.py
Exploratory Data Analysis + a simple traffic forecast for the
Website Traffic Analysis & Forecasting project.

Run:  python notebooks/eda_and_forecast.py
Outputs: PNG charts saved to ../charts/
"""
import sqlite3
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

DB_PATH = "traffic.db"
CHARTS_DIR = "charts"

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM website_traffic", conn, parse_dates=["date"])
conn.close()

# ---------------------------------------------------------------
# 1. Data cleaning / sanity checks
# ---------------------------------------------------------------
print("Missing values per column:\n", df.isna().sum())
print("\nRow count:", len(df))
df = df.drop_duplicates(subset="date")
df = df.sort_values("date").reset_index(drop=True)

# ---------------------------------------------------------------
# 2. Daily sessions trend + 7-day rolling average
# ---------------------------------------------------------------
daily = df.groupby("date", as_index=False)["sessions"].sum()
daily["rolling_7d"] = daily["sessions"].rolling(7).mean()

plt.figure(figsize=(11, 5))
plt.plot(daily["date"], daily["sessions"], alpha=0.3, label="Daily sessions")
plt.plot(daily["date"], daily["rolling_7d"], color="#154C79", linewidth=2, label="7-day rolling avg")
plt.title("Website Sessions Over Time (2024–2025)")
plt.xlabel("Date"); plt.ylabel("Sessions"); plt.legend()
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/01_daily_sessions_trend.png", dpi=130)
plt.close()

# ---------------------------------------------------------------
# 3. Channel performance
# ---------------------------------------------------------------
channel_perf = df.groupby("channel").agg(
    total_sessions=("sessions", "sum"),
    total_conversions=("conversions", "sum"),
).reset_index()
channel_perf["conversion_rate_pct"] = (
    100 * channel_perf["total_conversions"] / channel_perf["total_sessions"]
).round(2)
channel_perf = channel_perf.sort_values("total_sessions", ascending=False)
print("\nChannel performance:\n", channel_perf)

plt.figure(figsize=(8, 5))
plt.bar(channel_perf["channel"], channel_perf["total_sessions"], color="#154C79")
plt.title("Total Sessions by Channel")
plt.ylabel("Sessions"); plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/02_sessions_by_channel.png", dpi=130)
plt.close()

# ---------------------------------------------------------------
# 4. Weekday vs weekend pattern
# ---------------------------------------------------------------
df["day_type"] = np.where(df["date"].dt.weekday >= 5, "Weekend", "Weekday")
daytype_perf = df.groupby("day_type")["sessions"].mean().round(0)
print("\nAvg sessions, weekday vs weekend:\n", daytype_perf)

# ---------------------------------------------------------------
# 5. Simple forecast: next 30 days using linear trend + weekly seasonality
#    (kept intentionally simple/explainable for an interview walkthrough,
#     rather than a black-box model)
# ---------------------------------------------------------------
daily["t"] = np.arange(len(daily))
daily["weekday"] = daily["date"].dt.weekday

X = daily[["t", "weekday"]].copy()
X = pd.get_dummies(X, columns=["weekday"], drop_first=True)
y = daily["sessions"]

model = LinearRegression()
model.fit(X, y)

future_dates = pd.date_range(daily["date"].max() + pd.Timedelta(days=1), periods=30)
future = pd.DataFrame({
    "t": np.arange(len(daily), len(daily) + 30),
    "weekday": future_dates.weekday,
})
future_X = pd.get_dummies(future, columns=["weekday"], drop_first=True)
future_X = future_X.reindex(columns=X.columns, fill_value=0)
forecast = model.predict(future_X)

forecast_df = pd.DataFrame({"date": future_dates, "forecast_sessions": forecast.round(0)})
forecast_df.to_csv("data/traffic_forecast_next_30_days.csv", index=False)
print("\nForecast (first 5 rows):\n", forecast_df.head())

plt.figure(figsize=(11, 5))
plt.plot(daily["date"], daily["sessions"], alpha=0.3, label="Historical sessions")
plt.plot(forecast_df["date"], forecast_df["forecast_sessions"], color="#C0392B",
          linewidth=2, label="30-day forecast")
plt.title("Website Traffic Forecast — Next 30 Days")
plt.xlabel("Date"); plt.ylabel("Sessions"); plt.legend()
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/03_traffic_forecast.png", dpi=130)
plt.close()

# ---------------------------------------------------------------
# 6. Export a clean summary CSV for the Power BI dashboard
# ---------------------------------------------------------------
monthly = df.copy()
monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
monthly_summary = monthly.groupby("month").agg(
    sessions=("sessions", "sum"),
    users=("users", "sum"),
    conversions=("conversions", "sum"),
    avg_bounce_rate=("bounce_rate_pct", "mean"),
).reset_index()
monthly_summary.to_csv("data/monthly_summary_for_powerbi.csv", index=False)

print("\nAll charts saved to charts/. Power BI-ready CSVs saved to data/.")
