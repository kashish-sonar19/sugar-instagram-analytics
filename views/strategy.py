"""Task 10 – Strategic recommendations (full dataset)."""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src import theme as T
from src.data import summarise
from src.state import get_data

T.header("Recommendations", "Task 10 · data-driven strategy (uses all 50,000 posts, ignores sidebar filters)")
posts, _ = get_data()

# What do the top-25% posts have in common?
st.subheader("What do the top 25% posts have in common?")
st.caption("Representation index = share of a category among top-quartile posts ÷ its share among all posts × 100. "
           "Above 100 means it appears more often in the best posts than you'd expect.")
top = posts[posts["Performance Band"] == "Top 25%"]
rows = []
for dim in ["Post Type", "Campaign Type", "Engagement Source", "Day"]:
    rep = top[dim].astype(str).value_counts(normalize=True) / posts[dim].astype(str).value_counts(normalize=True) * 100
    rows += [{"Dimension": dim, "Category": k, "Index": v} for k, v in rep.items()]
rep = pd.DataFrame(rows)
rep["Diff"] = rep["Index"] - 100
chart = alt.Chart(rep).mark_bar(size=14).encode(
    y=alt.Y("Category:N", sort="-x", title=None),
    x=alt.X("Diff:Q", title="Representation in top 25% vs expected (index − 100)"),
    color=alt.condition("datum.Diff >= 0", alt.value(T.ACCENT), alt.value(T.NEG)),
    tooltip=["Dimension", "Category", alt.Tooltip("Index:Q", format=".1f")],
).properties(width=420, height=170).facet(facet=alt.Facet("Dimension:N", title=None), columns=2)
st.altair_chart(chart.resolve_scale(y="independent"), theme=None)

c = summarise(posts, ["Post Type", "Campaign Type"]).nlargest(5, "ER %")
st.markdown("**Best format × campaign combinations (weighted ER)**")
st.dataframe(c[["Post Type", "Campaign Type", "Posts", "ER %", "Save Rate %", "Share Rate %"]].round(3), hide_index=True)

st.divider()
report = Path(__file__).resolve().parents[1] / "docs" / "Insights_Report.md"
if report.exists():
    st.markdown(report.read_text(encoding="utf-8").split("\n", 1)[1])
