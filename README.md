# Sugar Cosmetics: Instagram Content Performance Dashboard

An interactive analytics dashboard that studies 50,000 Sugar Cosmetics Instagram posts (April 2024 to April 2025), identifies what drives engagement, and converts the findings into a practical posting playbook.

**Live app:** https://sugar-instagram-analytics-kdgpetfvashgnysavl6lrx.streamlit.app/

**Author:** Kashish Haresh Sonar
**Program:** Labmentrix Data Analytics Project
**Stack:** Python, Streamlit, Altair, Pandas (Altair and Streamlit used as the approved alternative to Tableau)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Dashboard Pages](#dashboard-pages)
4. [Metric Definitions](#metric-definitions)
5. [Mapping to the Project Brief](#mapping-to-the-project-brief)
6. [Folder Structure](#folder-structure)
7. [Getting Started](#getting-started)
8. [Documentation and Deliverables](#documentation-and-deliverables)
9. [Author](#author)

---

## Project Overview

Sugar Cosmetics publishes a high volume of Instagram content across formats, campaigns and posting days. This project answers a simple business question: **which content choices actually lift engagement, and how should the team post going forward?**

The analysis covers:

- Account-level KPIs and the monthly posting trend
- The best-performing posts by likes and by engagement rate
- Post format comparison (which format earns the most engagement per reach)
- Best days to post, including a day-by-format heatmap
- The engagement funnel from reach to likes, comments, shares and saves
- Hashtag usage, lift and combinations
- A fully interactive dashboard with cross-filtering
- A recommendations page that turns all of the above into actions

## Key Features

- **Multipage Streamlit app** with a shared set of sidebar filters (Format, Month, Hashtag, Campaign, Source) that apply across pages.
- **Click-to-filter dashboard:** click a Format, Day or Campaign bar and every other chart on the page updates.
- **Weighted engagement rate** so that high-reach posts count proportionally more than low-reach posts.
- **ER Index** to compare any group against the account average at a glance.
- **Hidden gem detection** on the Top Posts page using a reach-floor slider, to surface posts with strong engagement despite modest reach.
- **Cleaned data export** to a four-sheet Excel workbook.
- **Built-in data quality page** documenting cleaning steps, validation checks and metric definitions.
- **Consistent dark theme** with a shared Altair styling layer.

## Dashboard Pages

| Page | What it shows |
|---|---|
| Interactive Dashboard | Cross-filtered view of the whole dataset; click chart bars to drill down |
| KPIs and Posting Trend | Headline KPIs, monthly posting trend, month-over-month change |
| Top Posts | Top 10 by likes (lollipop chart) and top 10 by engagement rate with reach floor |
| Post Formats | Format comparison with a metric switcher and indexed grouped bars |
| Best Days to Post | Weekday engagement rate, deviation from average, day by format heatmap |
| Engagement Funnel | Step-down funnel, stage-to-stage conversion, follower path |
| Hashtags | Usage donut, engagement lift per hashtag, hashtag combinations |
| Recommendations | Posting playbook based on the analysis |
| Data Quality | Cleaning steps, checks and metric definitions |

## Metric Definitions

| Metric | Definition |
|---|---|
| Engagements | Likes + Comments + Shares + Saves |
| Engagement Rate (KPI and group comparisons) | Sum of Engagements divided by Sum of Reach, multiplied by 100 |
| ER Index | Group ER divided by account ER, multiplied by 100 |
| Post name | Generated as `#ID Format - Campaign (date)` because the dataset has no caption column |

**Why a weighted engagement rate?** A post seen by 40,000 people should count for more than one seen by 2,000. The account-level weighted ER is **18.55%**, while the simple average of per-post ER is 18.54%, so the two approaches agree closely.

**Reading the ER Index:** a value of 100 means the group performs exactly at the account average; above 100 is better than average, below 100 is weaker.

## Mapping to the Project Brief

| Brief task | Where it lives |
|---|---|
| 1. KPI overview | KPIs and Posting Trend |
| 2. Monthly posting trend | KPIs and Posting Trend (line chart and month-over-month change) |
| 3. Top 10 posts by likes | Top Posts (lollipop chart and table) |
| 4. Top 10 posts by engagement rate | Top Posts (reach floor slider and hidden gem flag) |
| 5. Post type comparison | Post Formats (metric switcher and indexed grouped bars) |
| 6. Day of week analysis | Best Days to Post (weekday ER, deviation, day by format heatmap) |
| 7. Engagement funnel | Engagement Funnel (step-down funnel, stage conversion, follower path) |
| 8. Hashtag analysis | Hashtags (usage donut, lift, combinations) |
| 9. Final dashboard | Interactive Dashboard (cross-filtering and sidebar filters) |
| 10. Recommendations | Recommendations page, `docs/Insights_Report.md` and the presentation |

## Folder Structure

```
Kashish_Sugar_Instagram_Dashboard/
├── streamlit_app.py          # Entry point: multipage navigation and sidebar filters
├── requirements.txt          # Python dependencies
├── src/
│   ├── data.py               # Loading, cleaning, metrics, aggregation, Excel export
│   ├── state.py              # Cached data and shared filters
│   └── theme.py              # Dark theme, colours, Altair styling, UI helpers
├── views/                    # One file per page
│   ├── dashboard.py          # Task 9: interactive cross-filter dashboard
│   ├── overview.py           # Task 1 KPIs and Task 2 monthly trend
│   ├── top_posts.py          # Tasks 3 and 4
│   ├── formats.py            # Task 5
│   ├── timing.py             # Task 6
│   ├── funnel.py             # Task 7
│   ├── hashtags.py           # Task 8
│   ├── strategy.py           # Task 10
│   └── data_quality.py       # Cleaning steps, checks, definitions
├── data/
│   └── raw/
│       └── sugar_cosmetics_instagram_data.csv
├── outputs/
│   └── sugar_instagram_clean.xlsx          # Cleaned data (4 sheets)
├── docs/
│   ├── Insights_Report.md                  # Business summary and recommendations
│   └── VIVA_NOTES.md                       # How to present the project
└── presentation/
    ├── Kashish_Sugar_Instagram_Presentation.pptx   # 9 slides
    └── Kashish_Sugar_Instagram_Presentation.pdf
```

## Getting Started

### Option 1: Use the hosted app

Open the live dashboard here: https://sugar-instagram-analytics-kdgpetfvashgnysavl6lrx.streamlit.app/

### Option 2: Run locally in VS Code

1. Create and activate a virtual environment.

   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # Mac / Linux
   source .venv/bin/activate
   ```

2. Install the dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Start the app.

   ```bash
   streamlit run streamlit_app.py
   ```

### Optional: regenerate the cleaned data

Running the data module prints the data quality checks and regenerates `outputs/sugar_instagram_clean.xlsx`.

```bash
python -m src.data
```

## Documentation and Deliverables

| Deliverable | Location |
|---|---|
| Business summary and recommendations | `docs/Insights_Report.md` |
| Presentation notes for the viva | `docs/VIVA_NOTES.md` |
| Slide deck (9 slides) | `presentation/Kashish_Sugar_Instagram_Presentation.pptx` and `.pdf` |
| Cleaned dataset (4 sheets) | `outputs/sugar_instagram_clean.xlsx` |
| Live dashboard | https://sugar-instagram-analytics-kdgpetfvashgnysavl6lrx.streamlit.app/ |

## Author

**Kashish Haresh Sonar**
Labmentrix Data Analytics Project
