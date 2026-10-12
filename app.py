"""
Hotel Booking Revenue Dashboard — Team Insight
BANA409 In-Class Group Exercise.

Decision-maker: the hotel Revenue & Reservations Manager.
Run locally:  uv run streamlit run app.py
"""
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Hotel Revenue Dashboard", layout="wide")

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "hotel_bookings.csv")

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    month_num = df["arrival_date_month"].map({m: i for i, m in enumerate(MONTHS, start=1)})
    df["arrival_date"] = pd.to_datetime(
        dict(year=df["arrival_date_year"], month=month_num,
             day=df["arrival_date_day_of_month"]), errors="coerce")
    df["arrival_month"] = df["arrival_date"].dt.to_period("M").astype(str)
    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    # ADR data-quality flag: one record is 5,400 (clear entry error), one is negative.
    df["adr_valid"] = (df["adr"] >= 0) & (df["adr"] <= 1000)
    return df


df = load_data()

# ---------------------------------------------------------------- Filters
st.sidebar.header("Filters")
hotel_choice = st.sidebar.radio(
    "Hotel", ["All hotels", "City Hotel", "Resort Hotel"], index=0)
segments = sorted(df["market_segment"].dropna().unique().tolist())
seg_choice = st.sidebar.multiselect(
    "Market segment", segments, default=segments,
    help="The manager focuses on segments with high cancellation risk, e.g. Groups.")

mask = df["market_segment"].isin(seg_choice)
if hotel_choice != "All hotels":
    mask &= df["hotel"] == hotel_choice
d = df[mask]

st.sidebar.info(
    "Data: Jul 2015 - Aug 2017 (arrivals), Kaggle snapshot.\n\n"
    "Planned production refresh: nightly from the PMS/CRS; reviewed every "
    "Monday morning (daily in peak season).")

# ---------------------------------------------------------------- Header
st.title("Hotel Booking Revenue Dashboard — Team Insight")
st.caption(
    "For the hotel **Revenue & Reservations Manager**: see expected occupancy, "
    "cancellation risk and ADR by arrival month, then adjust pricing, overbooking "
    "and deposit/cancellation policy.")

if d.empty:
    st.warning("No bookings match the current filters. Please select at least one market segment.")
    st.stop()

# ---------------------------------------------------------------- KPI row
occupied_nights = int(d.loc[d["is_canceled"] == 0, "total_nights"].sum())
cancel_rate = float(d["is_canceled"].mean())
adr_value = float(d.loc[(d["is_canceled"] == 0) & d["adr_valid"], "adr"].mean())

k1, k2, k3 = st.columns(3)
k1.metric("Occupied room-nights", f"{occupied_nights:,}")
k2.metric("Cancellation rate", f"{cancel_rate:.1%}")
k3.metric("Avg. daily rate (ADR)", f"EUR {adr_value:,.0f}")
st.caption(
    "Occupied room-nights count non-canceled bookings only. ADR excludes one "
    "invalid record (EUR 5,400) and one negative value.")

# ---------------------------------------------------------------- Chart 1
non_canceled = d[d["is_canceled"] == 0]
monthly = pd.DataFrame({
    "occupied_nights": non_canceled.groupby("arrival_month")["total_nights"].sum(),
    "adr": d[d["adr_valid"]].groupby("arrival_month")["adr"].mean(),
    "bookings": d.groupby("arrival_month").size(),
    "cancel_rate": d.groupby("arrival_month")["is_canceled"].mean(),
}).reset_index().sort_values("arrival_month")

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=monthly["arrival_month"], y=monthly["occupied_nights"],
    name="Occupied room-nights", marker_color="#4C78A8"))
fig1.add_trace(go.Scatter(
    x=monthly["arrival_month"], y=monthly["adr"], name="ADR (EUR)",
    mode="lines+markers", yaxis="y2",
    line=dict(color="#E45756", width=3)))
fig1.update_layout(
    title="Occupied room-nights and ADR by arrival month",
    yaxis=dict(title="Occupied room-nights"),
    yaxis2=dict(title="ADR (EUR)", overlaying="y", side="right", showgrid=False),
    legend=dict(orientation="h", y=1.12),
    margin=dict(l=10, r=10, t=50, b=10), height=430)
st.plotly_chart(fig1, use_container_width=True)

# ---------------------------------------------------------------- Chart 2
seg = (d.groupby("market_segment")
       .agg(cancel_rate=("is_canceled", "mean"), n=("is_canceled", "size"))
       .reset_index())
seg = seg[seg["n"] >= 100].sort_values("cancel_rate")

fig2 = px.bar(
    seg, x="cancel_rate", y="market_segment", orientation="h",
    labels={"cancel_rate": "Cancellation rate", "market_segment": ""},
    text="cancel_rate")
fig2.update_traces(marker_color="#E45756", texttemplate="%{text:.0%}",
                   textposition="outside")
fig2.update_layout(
    title="Cancellation rate by market segment (segments with 100+ bookings)",
    xaxis=dict(tickformat=".0%", title="Cancellation rate"),
    margin=dict(l=10, r=40, t=50, b=10), height=380, showlegend=False)
fig2.add_vline(x=cancel_rate, line_dash="dash", line_color="#555555",
               annotation_text="selected overall", annotation_position="top")
st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------------- Detail
with st.expander("Monthly detail (for deeper investigation)"):
    show = monthly.copy()
    show["adr"] = show["adr"].round(1)
    show["cancel_rate"] = show["cancel_rate"].round(3)
    st.dataframe(
        show.rename(columns={
            "arrival_month": "Arrival month",
            "occupied_nights": "Occupied room-nights",
            "adr": "ADR (EUR)", "bookings": "Bookings",
            "cancel_rate": "Cancellation rate"}),
        use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- Footer
st.caption(
    "Data period: Jul 2015 - Aug 2017 (arrivals), Kaggle snapshot "
    "(jessemostipak/hotel-booking-demand). Intended production refresh: nightly "
    "from the PMS/CRS, reviewed every Monday morning (daily in peak season). "
    "Same-day alert when expected occupancy for arrivals within the next 4 weeks "
    "falls more than 10 percentage points versus four weeks prior, or Groups "
    "cancellation exceeds 50%.")
