"""Data quality checks, method and data dictionary."""

import pandas as pd
import streamlit as st

from src import theme as T
from src.data import RAW_FILE, quality_report
from src.state import filtered, get_data

T.header("Data & Method", "How the raw file was checked, cleaned and enriched")


@st.cache_data
def raw_checks():
    return quality_report(pd.read_csv(RAW_FILE))


c1, c2 = st.columns([1, 1.4])
with c1:
    st.markdown("#### Quality checks on the raw file")
    st.dataframe(raw_checks(), hide_index=True)
with c2:
    st.markdown("#### Cleaning & feature engineering")
    st.markdown("""
1. Trimmed column names and text values; converted **Post Date** to a date and metrics to numbers.
2. Dropped rows with missing dates/metrics, zero reach, or reach above impressions (none found).
3. Removed duplicate rows (none found) and sorted posts by date.
4. Added a readable **Post Name** — the data has no caption column.
5. Added **Month**, **Day** and **Is Weekend** for trend and timing analysis.
6. Calculated **Engagements**, **ER %**, save / share / comment / follow rates.
7. Split the comma-separated **Hashtags** into a list (one row per hashtag for Task 8).
8. Grouped posts into **Performance Bands** (ER quartiles).
""")

st.markdown("#### Metric definitions")
st.dataframe(pd.DataFrame([
    ("Engagements", "Likes + Comments + Shares + Saves"),
    ("ER % (per post)", "Engagements ÷ Reach × 100"),
    ("Engagement rate (KPI / groups)", "Σ Engagements ÷ Σ Reach × 100 — weighted, so big-reach posts count proportionally"),
    ("ER Index", "Group ER ÷ account ER × 100 (100 = average)"),
    ("Save / Share / Follow rate", "Saves, Shares or Follows ÷ Reach × 100"),
    ("Lift (pp)", "Group ER − account ER, in percentage points"),
], columns=["Metric", "Formula"]), hide_index=True)

df, _ = filtered()
st.markdown(f"#### Cleaned data preview ({len(df):,} posts after filters)")
show = df.drop(columns=["Tag List"]).head(300).copy()
show["Day"] = show["Day"].astype(str)
show["Post Date"] = show["Post Date"].dt.date
st.dataframe(show, hide_index=True)
export = df.drop(columns=["Tag List"]).copy()
export["Day"] = export["Day"].astype(str)
st.download_button("Download filtered posts (CSV)", export.to_csv(index=False).encode(),
                   "sugar_instagram_filtered.csv", "text/csv")
st.caption("Full cleaned workbook: outputs/sugar_instagram_clean.xlsx (regenerate with `python -m src.data`).")
