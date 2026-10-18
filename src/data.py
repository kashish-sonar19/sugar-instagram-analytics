"""
Data layer for the Sugar Cosmetics Instagram dashboard.

- load_posts()      -> cleaned post-level table with engineered metrics
- hashtag_table()   -> one row per (post, hashtag)
- summarise()       -> weighted metrics for any grouping
- build_cube()      -> pre-aggregated table used by the interactive Altair dashboard

Run `python -m src.data` from the project folder to export the cleaned
workbook to outputs/sugar_instagram_clean.xlsx
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "data" / "raw" / "sugar_cosmetics_instagram_data.csv"
OUTPUT_DIR = BASE_DIR / "outputs"

DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
FUNNEL_STAGES = ["Impressions", "Reach", "Likes", "Comments", "Shares", "Saves"]
NUMERIC = ["Impressions", "Reach", "Likes", "Comments", "Shares", "Saves",
           "Profile Visits", "Follows"]


# ----------------------------------------------------------------------------
# Cleaning
# ----------------------------------------------------------------------------
def quality_report(raw: pd.DataFrame) -> pd.DataFrame:
    """Simple data-quality checklist shown on the Data Quality page."""
    checks = [
        ("Rows", f"{len(raw):,}"),
        ("Columns", raw.shape[1]),
        ("Missing values", int(raw.isna().sum().sum())),
        ("Duplicate rows", int(raw.duplicated().sum())),
        ("Unparseable dates", int(pd.to_datetime(raw["Post Date"], errors="coerce").isna().sum())),
        ("Negative metric values", int((raw[NUMERIC] < 0).sum().sum())),
        ("Reach greater than Impressions", int((raw["Reach"] > raw["Impressions"]).sum())),
        ("Likes greater than Reach", int((raw["Likes"] > raw["Reach"]).sum())),
    ]
    return pd.DataFrame([(c, str(v)) for c, v in checks], columns=["Check", "Result"])


def load_posts(path: Path = RAW_FILE) -> pd.DataFrame:
    raw = pd.read_csv(path)
    df = raw.rename(columns=lambda c: c.strip()).copy()

    # types
    df["Post Date"] = pd.to_datetime(df["Post Date"], errors="coerce")
    text_cols = ["Post Type", "Campaign Type", "Hashtags", "Audience Emotion", "Engagement Source"]
    df[text_cols] = df[text_cols].apply(lambda s: s.astype(str).str.strip())
    df[NUMERIC] = df[NUMERIC].apply(pd.to_numeric, errors="coerce")

    # remove rows that cannot be analysed
    df = df.dropna(subset=["Post Date"] + NUMERIC)
    df = df[(df["Reach"] > 0) & (df["Reach"] <= df["Impressions"])]
    df = df.drop_duplicates().sort_values("Post Date").reset_index(drop=True)

    # identifiers (no caption column in the data)
    df["Post No"] = np.arange(1, len(df) + 1)
    df["Post Name"] = ("#" + df["Post No"].astype(str).str.zfill(5) + " " + df["Post Type"]
                       + " – " + df["Campaign Type"] + " (" + df["Post Date"].dt.strftime("%d-%b-%y") + ")")

    # calendar fields
    df["Month"] = df["Post Date"].dt.strftime("%Y-%m")
    df["Month Name"] = df["Post Date"].dt.strftime("%b-%y")
    df["Day"] = pd.Categorical(df["Post Date"].dt.strftime("%a"), DAY_ORDER, ordered=True)
    df["Is Weekend"] = df["Day"].isin(["Sat", "Sun"])

    # engagement metrics
    df["Engagements"] = df["Likes"] + df["Comments"] + df["Shares"] + df["Saves"]
    df["ER %"] = df["Engagements"] / df["Reach"] * 100
    df["ER by Impressions %"] = df["Engagements"] / df["Impressions"] * 100
    df["Save Rate %"] = df["Saves"] / df["Reach"] * 100
    df["Share Rate %"] = df["Shares"] / df["Reach"] * 100
    df["Comment Rate %"] = df["Comments"] / df["Reach"] * 100
    df["Follow Rate %"] = df["Follows"] / df["Reach"] * 100

    # hashtags
    df["Tag List"] = df["Hashtags"].str.split(",").apply(lambda xs: sorted(x.strip() for x in xs if x.strip()))
    df["No. of Hashtags"] = df["Tag List"].str.len()

    # performance band (quartiles of ER)
    df["Performance Band"] = pd.qcut(df["ER %"], 4, labels=["Bottom 25%", "Lower-mid", "Upper-mid", "Top 25%"])
    return df


def hashtag_table(df: pd.DataFrame) -> pd.DataFrame:
    keep = ["Post No", "Post Type", "Campaign Type", "Engagement Source", "Month", "Day",
            "Reach", "Impressions", "Engagements", "Likes", "Comments", "Shares", "Saves", "Tag List"]
    long = df[keep].explode("Tag List").rename(columns={"Tag List": "Hashtag"})
    return long.dropna(subset=["Hashtag"]).reset_index(drop=True)


# ----------------------------------------------------------------------------
# Aggregation helpers
# ----------------------------------------------------------------------------
def summarise(df: pd.DataFrame, by) -> pd.DataFrame:
    """Weighted metrics per group: rates are computed from totals (Σ / Σ)."""
    sums = ["Impressions", "Reach", "Likes", "Comments", "Shares", "Saves", "Follows", "Engagements"]
    g = df.groupby(by, observed=True).agg(Posts=("Reach", "size"), **{c: (c, "sum") for c in sums})
    g["ER %"] = g["Engagements"] / g["Reach"] * 100
    g["Save Rate %"] = g["Saves"] / g["Reach"] * 100
    g["Share Rate %"] = g["Shares"] / g["Reach"] * 100
    g["Follow Rate %"] = g["Follows"] / g["Reach"] * 100
    overall = df["Engagements"].sum() / df["Reach"].sum() * 100
    g["ER Index"] = g["ER %"] / overall * 100          # 100 = account average
    return g.reset_index()


def weighted_er(df: pd.DataFrame) -> float:
    return df["Engagements"].sum() / df["Reach"].sum() * 100 if len(df) else float("nan")


def build_cube(df: pd.DataFrame) -> pd.DataFrame:
    """Pre-aggregated table (~7k rows) for the client-side interactive dashboard."""
    dims = ["Post Type", "Day", "Month", "Campaign Type", "Engagement Source"]
    sums = ["Impressions", "Reach", "Likes", "Comments", "Shares", "Saves", "Engagements"]
    cube = df.groupby(dims, observed=True).agg(Posts=("Reach", "size"), **{c: (c, "sum") for c in sums})
    cube = cube.reset_index()
    cube["Day"] = cube["Day"].astype(str)
    return cube


def export_workbook(df: pd.DataFrame, path: Path | None = None) -> Path:
    path = path or OUTPUT_DIR / "sugar_instagram_clean.xlsx"
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = df.drop(columns=["Tag List"]).copy()
    clean["Post Date"] = clean["Post Date"].dt.date
    clean["Day"] = clean["Day"].astype(str)
    tags = hashtag_table(df)
    tags["Day"] = tags["Day"].astype(str)
    monthly = summarise(df, ["Month"])
    kpis = pd.DataFrame({
        "KPI": ["Total posts", "Total likes", "Total comments", "Total reach",
                "Weighted engagement rate %", "Mean post engagement rate %"],
        "Value": [len(df), df["Likes"].sum(), df["Comments"].sum(), df["Reach"].sum(),
                  round(weighted_er(df), 3), round(df["ER %"].mean(), 3)],
    })
    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        kpis.to_excel(xl, sheet_name="kpi_summary", index=False)
        clean.round(3).to_excel(xl, sheet_name="clean_posts", index=False)
        tags.to_excel(xl, sheet_name="hashtag_level", index=False)
        monthly.round(3).to_excel(xl, sheet_name="monthly_summary", index=False)
    return path


if __name__ == "__main__":
    raw = pd.read_csv(RAW_FILE)
    print(quality_report(raw).to_string(index=False))
    posts = load_posts()
    print(f"\nClean posts: {len(posts):,}  |  weighted ER: {weighted_er(posts):.2f}%")
    print("Saved:", export_workbook(posts))
