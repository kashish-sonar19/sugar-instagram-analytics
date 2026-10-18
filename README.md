# Sugar Cosmetics – Instagram Content Performance Dashboard

**Author:** Kashish Haresh Sonar · Labmentrix Data Analytics Project  
**Tool:** Streamlit + Altair (approved alternative to Tableau)

The project analyses 50,000 Sugar Cosmetics Instagram posts (Apr 2024 – Apr 2025) to find what drives engagement, and turns the results into a posting playbook.

## Folder structure

```
Kashish_Sugar_Instagram_Dashboard/
├── streamlit_app.py          # entry point – multipage navigation + sidebar filters
├── src/
│   ├── data.py               # loading, cleaning, metrics, aggregation, Excel export
│   ├── state.py              # cached data + shared filters
│   └── theme.py              # dark theme, colours, Altair styling, UI helpers
├── views/                    # one file per page
│   ├── dashboard.py          # Task 9 – interactive cross-filter dashboard
│   ├── overview.py           # Task 1 KPIs + Task 2 monthly trend
│   ├── top_posts.py          # Task 3 + Task 4
│   ├── formats.py            # Task 5
│   ├── timing.py             # Task 6
│   ├── funnel.py             # Task 7
│   ├── hashtags.py           # Task 8
│   ├── strategy.py           # Task 10
│   └── data_quality.py       # cleaning steps, checks, definitions
├── data/raw/sugar_cosmetics_instagram_data.csv
├── outputs/sugar_instagram_clean.xlsx      # cleaned data (4 sheets)
├── docs/
│   ├── Insights_Report.md                  # business summary + recommendations
│   └── VIVA_NOTES.md                       # how to present the project
└── presentation/
    ├── Kashish_Sugar_Instagram_Presentation.pptx   # 9 slides
    └── Kashish_Sugar_Instagram_Presentation.pdf
```

## Run in VS Code

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Optional: `python -m src.data` prints the data-quality checks and regenerates `outputs/sugar_instagram_clean.xlsx`.

## How the brief maps to the app

| Brief task | Page |
|---|---|
| 1 KPI overview | KPIs & Posting Trend |
| 2 Monthly posting trend | KPIs & Posting Trend (line + month-over-month change) |
| 3 Top 10 by likes | Top Posts (lollipop chart + table) |
| 4 Top 10 by engagement rate | Top Posts (reach floor slider, "hidden gem" flag) |
| 5 Post type comparison | Post Formats (metric switcher + indexed grouped bars) |
| 6 Day of week | Best Days to Post (weekday ER, deviation, day × format heatmap) |
| 7 Engagement funnel | Engagement Funnel (step-down funnel, stage conversion, follower path) |
| 8 Hashtag analysis | Hashtags (usage donut, lift, combinations) |
| 9 Final dashboard | Interactive Dashboard: click Format / Day / Campaign bars to cross-filter everything; sidebar filters for Format, Month, Hashtag, Campaign, Source |
| 10 Recommendations | Recommendations page + `docs/Insights_Report.md` + presentation |

## Metric choices

- **Engagements** = Likes + Comments + Shares + Saves
- **Engagement rate (KPI and group comparisons)** = Σ Engagements ÷ Σ Reach × 100. This is a *weighted* rate, so a post seen by 40K people counts more than one seen by 2K. The account value is **18.55%**; the simple average of post ERs is 18.54%.
- **ER Index** = group ER ÷ account ER × 100. A value of 100 means the group performs at the account average.
- Post names are generated as `#ID Format – Campaign (date)` because the dataset has no caption column.
