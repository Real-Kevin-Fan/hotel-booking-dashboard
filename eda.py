"""Quick EDA for the Hotel Booking Demand dataset (BANA409 in-class exercise).

Run with:
    uv run --with pandas --with matplotlib eda.py
"""
import os
import pandas as pd
import numpy as np

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 50)

DATA = os.path.join(os.path.dirname(__file__), "data", "hotel_bookings.csv")
df = pd.read_csv(DATA)

print("=" * 70)
print("SHAPE:", df.shape)
print("=" * 70)
print("\nDTYPES:")
print(df.dtypes)

print("\n" + "=" * 70)
print("MISSING VALUES (non-zero only):")
miss = df.isna().sum()
print(miss[miss > 0])

# Build a proper arrival date
month_map = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"], start=1)}
df["arrival_month_num"] = df["arrival_date_month"].map(month_map)
df["arrival_date"] = pd.to_datetime(
    dict(year=df["arrival_date_year"], month=df["arrival_month_num"],
         day=df["arrival_date_day_of_month"]), errors="coerce")

print("\n" + "=" * 70)
print("ARRIVAL DATE RANGE:", df["arrival_date"].min(), "->", df["arrival_date"].max())

print("\n--- hotel ---")
print(df["hotel"].value_counts())
print("\n--- arrival_date_year ---")
print(df["arrival_date_year"].value_counts().sort_index())
print("\n--- is_canceled (overall rate) ---")
print(df["is_canceled"].value_counts())
print("cancellation rate: {:.3f}".format(df["is_canceled"].mean()))
print("\n--- cancellation rate by hotel ---")
print(df.groupby("hotel")["is_canceled"].mean().round(3))

print("\n--- market_segment ---")
print(df["market_segment"].value_counts())
print("\n--- distribution_channel ---")
print(df["distribution_channel"].value_counts())
print("\n--- customer_type ---")
print(df["customer_type"].value_counts())
print("\n--- top 12 countries ---")
print(df["country"].value_counts().head(12))

print("\n" + "=" * 70)
print("NUMERIC SUMMARY (key fields):")
nums = ["lead_time", "stays_in_weekend_nights", "stays_in_week_nights",
        "adults", "children", "babies", "adr", "booking_changes",
        "days_in_waiting_list", "total_of_special_requests",
        "previous_cancellations", "previous_bookings_not_canceled",
        "is_repeated_guest", "required_car_parking_spaces"]
print(df[nums].describe().round(2).T)

# Derived fields
df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
df["guests"] = df["adults"].fillna(0) + df["children"].fillna(0) + df["babies"].fillna(0)
# Revenue only counts bookings that were NOT canceled (check-out / check-out-like)
df["estimated_revenue"] = np.where(df["is_canceled"] == 0, df["adr"] * df["total_nights"], 0.0)

print("\n--- total_nights distribution ---")
print(df["total_nights"].describe().round(2))
print("bookings with 0 nights:", (df["total_nights"] == 0).sum())
print("bookings with 0 guests:", (df["guests"] == 0).sum())

print("\n--- adr anomalies ---")
print("adr < 0:", (df["adr"] < 0).sum())
print("adr > 1000:")
print(df.loc[df["adr"] > 1000, ["hotel", "arrival_date_year", "arrival_date_month",
                                "adults", "children", "babies", "total_nights", "adr"]])

# Monthly trend (by arrival month)
print("\n" + "=" * 70)
print("MONTHLY TREND (by arrival month):")
g = df.groupby([df["arrival_date"].dt.to_period("M")]).agg(
    bookings=("hotel", "size"),
    cancellations=("is_canceled", "sum"),
    cancel_rate=("is_canceled", "mean"),
    adr=("adr", "mean"),
    occupied_nights=("total_nights", lambda s: s[df.loc[s.index, "is_canceled"] == 0].sum()),
    revenue=("estimated_revenue", "sum"),
)
g["adr"] = g["adr"].round(1)
g["cancel_rate"] = g["cancel_rate"].round(3)
g["revenue"] = g["revenue"].round(0)
print(g.to_string())

print("\n" + "=" * 70)
print("HEADLINE CANDIDATES (full dataset):")
print("total bookings:", len(df))
print("overall cancel rate: {:.3f}".format(df["is_canceled"].mean()))
print("mean ADR (all): {:.1f}".format(df["adr"].mean()))
print("mean ADR (non-canceled, adr>=0): {:.1f}".format(
    df.loc[(df["is_canceled"] == 0) & (df["adr"] >= 0), "adr"].mean()))
print("total occupied room-nights:", int(df.loc[df["is_canceled"] == 0, "total_nights"].sum()))
print("total estimated revenue: {:,.0f}".format(df["estimated_revenue"].sum()))
print("median lead time:", df["lead_time"].median())

# Cancellation by market segment
print("\n--- cancel rate by market_segment ---")
print(df.groupby("market_segment")["is_canceled"].agg(["mean", "size"]).round(3).sort_values("mean", ascending=False))

# Lead time vs cancellation
print("\n--- cancel rate by lead-time bucket ---")
bins = [-1, 7, 30, 90, 180, 1000]
labels = ["0-7d", "8-30d", "31-90d", "91-180d", "180d+"]
print(df.groupby(pd.cut(df["lead_time"], bins=bins, labels=labels), observed=True)
      ["is_canceled"].mean().round(3))
print("\nEDA complete.")
