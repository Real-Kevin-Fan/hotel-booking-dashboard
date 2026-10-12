# Hotel Booking Revenue Dashboard — Team Insight

A focused Streamlit dashboard for the **BANA409 In-Class Group Exercise**. It turns
the Kaggle *Hotel Booking Demand* dataset into a weekly working tool for a hotel
**Revenue & Reservations Manager**, rather than a page crowded with every chart the
data allows.

- **Deployed app:** _added after Streamlit Cloud deployment_
- **Kaggle dataset:** https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand
- **Python:** 3.14 · managed with [`uv`](https://docs.astral.sh/uv/)

---

## Step 1 — Dataset and Decision-Maker

### The dataset

**Hotel Booking Demand** (`hotel_bookings.csv`, one CSV, ~16 MB / 119,390 rows —
comfortably under the 25 MB limit).

- **Origin / real or synthetic:** real booking records extracted from the property
  management systems (PMS) of two hotels in Portugal — one resort hotel and one city
  hotel — then anonymized. The data is documented in the peer-reviewed data article
  Antonio, Almeida & Nunes, *"Hotel booking demand datasets,"* **Data in Brief**, 2019
  (ScienceDirect). It is not a generated or teaching dataset.
- **Period covered:** arrivals from **July 2015 through August 2017**. Note that 2015
  contains only July–December and 2017 only January–August, so full-year totals for
  those years are not comparable to 2016.
- **What one row is:** one hotel booking (a reservation), with its hotel, arrival date,
  length of stay, guests, country of origin, market segment and distribution channel,
  lead time, quoted average daily rate (ADR), deposit type, and whether it was later
  canceled.
- **File handling:** the Kaggle download is a small `archive.zip`; it was unzipped to
  `data/hotel_bookings.csv`. No sampling or aggregation was needed — the single CSV is
  already below 25 MB. The committed file is the full, un-sampled dataset.

This is **not** Iris, Titanic, the world-cities data, or the California housing data.

### The decision-maker

The dashboard is built for **one role: the hotel Revenue & Reservations Manager** — the
person who sets room prices, controls how much inventory is opened to each channel,
manages group blocks, sets deposit and cancellation rules, and decides overbooking
levels. It is deliberately not built for "everyone": front-desk staff, marketing, and
ownership would each need different numbers.

---

## Step 2 — Justify the Dashboard

1. **Who looks at it, and how often?** The Revenue & Reservations Manager reviews it
   **every Monday morning** ahead of the weekly revenue meeting, when pricing and
   inventory for the next 4–12 weeks are set. During the June–August peak it is checked
   briefly each day.

2. **What decision does it support?**
   > *"If the manager sees the expected occupied room-nights for a future arrival month
   > fall below plan — driven by a cancellation rate well above the same period last
   > year, especially for long-lead and **Groups** business — she will tighten deposit
   > and cancellation terms for those dates, adjust the overbooking ratio, and re-price
   > remaining rooms (discounting slow dates, raising price on dates that still sell)."*

   The dashboard is built so this sentence can be finished in the first minute of use.

3. **What do they do today, and what does it cost?** Today the manager exports PMS data
   to Excel and rebuilds pivot tables by hand each week — a few hours of work that is
   error-prone and always a step behind. The cost is not just that time. Hotel rooms are
   perishable: an unsold night can never be sold again. With **37% of bookings canceled
   overall (42% at the city hotel; 61% of Groups)**, cancellations that are noticed late
   leave rooms that could have been resold, which is a direct, permanent loss of room
   revenue. Manual reporting also makes it easy to count canceled bookings as if they
   were still arriving.

4. **Why a dashboard rather than an email, a report, or an alert?** The *same* questions
   — expected occupancy, cancellation risk, and ADR by arrival month and segment — recur
   every week and lead directly to action, which is exactly when a dashboard earns its
   place. A weekly email or slide deck cannot be filtered by hotel or segment or used to
   dig into a specific month. A standalone alert answers one question but gives no
   context for *why* a number moved. The dashboard provides the recurring, interactive
   overview; alerts (Step 4) handle the few things that cannot wait for Monday.

---

## Step 3 — Decide What Matters

A quick EDA (`eda.py`) covered shape, data types, missing values, distributions, and
relationships. The dashboard then keeps only what changes the manager's decision.

### Three headline numbers (`st.metric`, one row)

The manager should answer *"is anything wrong right now?"* within five seconds:

1. **Occupied room-nights** — total nights from bookings that were **not** canceled. The
   core volume measure.
2. **Cancellation rate** — the single biggest risk in this data (37% overall).
3. **Average daily rate (ADR, EUR)** — the price lever, computed on valid, non-canceled
   bookings.

Estimated room revenue (ADR × nights) is the product of the first and third metrics, so
it is not given a fourth tile: an extra headline number would dilute the three that
drive the weekly decision.

### Two supporting charts

- **Occupied room-nights and ADR by arrival month** (bars + line on a secondary axis):
  shows the strong seasonal pattern and the price–volume relationship — *why* a month is
  high or low.
- **Cancellation rate by market segment** (horizontal bars with the selected overall
  rate as a reference line): pinpoints *where* cancellation risk comes from — Groups
  (61%) and Online TA (37%) versus Direct (15%) — which points straight at the policy
  and channel response.

### Filters (only the ones the role uses)

- **Hotel** (All / City / Resort) — the manager may own one property or both.
- **Market segment** (multi-select) — the manager focuses on risk segments such as
  Groups. No decorative sliders were added.

### Two things deliberately NOT shown

- **Guest-country map / the long country breakdown.** Portugal, Britain, France, Spain
  and Germany dominate, but a choropleth is visually appealing without changing the
  weekly pricing or cancellation-policy decision, so it was cut.
- **Parking spaces and repeat-guest indicators.** Only ~3% of bookings are repeat guests
  and ~6% request parking; both are far too small to move a revenue decision. Meal plan
  and reserved-vs-assigned room type were also explored and set aside for the same
  reason.

### Things in the data that could mislead — and how they are handled

- **One invalid ADR of EUR 5,400** (a single one-night city-hotel booking in March
  2016 — plainly a data-entry error) and **one negative ADR (−6.4)** are flagged and
  excluded from ADR calculations; a caption says so explicitly.
- **Canceled bookings must not look like occupied business.** Occupied room-nights count
  non-canceled bookings only, and this definition is stated under the KPI row.
- **Incomplete end years.** 2015 (from July) and 2017 (to August) are partial, so the
  app trends by **month** and states the period rather than inviting misleading yearly
  totals.
- **The `company` column is missing for ~94% of rows** and is not used.
- **ADR is room price per day, not total revenue** and does not include extras; the
  dashboard labels it as ADR rather than implying it is total sales.

### Order of the page

People read top to bottom and often do not scroll, so the layout follows importance:
**(top)** title, who/what caption, and the three KPIs; **(middle)** the two charts that
explain why the numbers moved; **(bottom)** a collapsed monthly-detail table for anyone
who wants to dig in. Every element was tested against *"if this disappeared, would the
manager notice?"* — anything that failed was removed.

---

## Step 4 — Refresh Frequency

The Kaggle CSV is a frozen snapshot. For the real-world dashboard:

1. **Data refresh — nightly.** Reservations, cancellations, no-shows and rate changes
   are extracted from the PMS/CRS once a night. Real-time refresh would add integration
   cost without changing any decision, because pricing and inventory actions are taken
   on a weekly cadence, not minute to minute.
2. **Review — every Monday morning**, which is distinct from the nightly data refresh:
   the numbers update overnight so the manager opens a current page at the weekly
   revenue meeting. In peak season the same page gets a short daily look.
3. **What is tracked, and what triggers action.** The key tracked metric is **expected
   occupied room-nights for arrivals in the next four weeks**. A same-day alert fires
   when expected occupancy for those near-term dates falls **more than 10 percentage
   points versus four weeks prior**, or when **Groups cancellation exceeds 50%** for an
   upcoming block. Those are the conditions that require a phone call the same day
   rather than a Monday dashboard check.
4. **Cost of stale data.** One day late can mean missing the short window to resell
   rooms for dates that are about to arrive — and an empty night is revenue lost
   forever. A week late can hide an entire canceled group block, producing both large
   avoidable vacancies and prices set for demand that no longer exists.

The dashboard states its **data period** and this **intended production refresh
frequency** in the sidebar and footer, since the submitted data itself does not update.

---

## Step 5 — Build and Run

The app contains, as required: a title with the team name; a one-line caption of who it
is for and the decision it supports; a row of `st.metric` KPIs; two supporting charts;
two working filters; and the data-period / refresh-frequency line.

### Run locally

```bash
uv sync
uv run streamlit run app.py
```

### Deploy

Published to a public GitHub repository under the student's own account and deployed on
Streamlit Cloud, with the Python version set to **3.14** under **Advanced settings** and
the main file set to `app.py`.

### Repository structure

```
hotel-booking-dashboard/
├── app.py                 # Streamlit dashboard
├── eda.py                 # quick EDA used to make the Step 3 decisions
├── data/
│   ├── hotel_bookings.csv # full Kaggle dataset (~16 MB, un-sampled)
│   └── archive.zip        # original Kaggle download
├── pyproject.toml         # uv project, Python >=3.14
├── uv.lock
└── README.md              # written answers to Steps 1–4
```
