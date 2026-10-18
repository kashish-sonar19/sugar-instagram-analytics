"""Task 8 – Hashtag analysis."""

import altair as alt
import streamlit as st

from src import theme as T
from src.state import filtered, filter_caption

T.header("Hashtags", "Task 8 · which hashtags and combinations drive engagement?")
df, tags = filtered()
filter_caption(df)
if df.empty or tags.empty:
    st.stop()

overall = df["Engagements"].sum() / df["Reach"].sum() * 100
h = (tags.groupby("Hashtag").agg(Posts=("Post No", "nunique"), Reach=("Reach", "sum"),
                                 Engagements=("Engagements", "sum"), AvgReach=("Reach", "mean"))
     .reset_index())
h["ER %"] = h["Engagements"] / h["Reach"] * 100
h["Lift vs avg"] = h["ER %"] - overall
h["Usage %"] = h["Posts"] / h["Posts"].sum() * 100

c1, c2 = st.columns([1, 1.25])
donut = alt.Chart(h).mark_arc(innerRadius=65, stroke=T.SURFACE, strokeWidth=2).encode(
    theta="Posts:Q",
    color=alt.Color("Hashtag:N", scale=alt.Scale(range=["#199e70", "#c98500", "#9085e9", "#d55181", "#3987e5"]),
                    legend=alt.Legend(orient="right")),
    tooltip=["Hashtag", alt.Tooltip("Posts:Q", format=","), alt.Tooltip("Usage %:Q", format=".1f")])
c1.altair_chart(donut.properties(height=300, width="container", title="Share of hashtag usage"), theme=None)

lift = alt.Chart(h).mark_bar(size=26).encode(
    y=alt.Y("Hashtag:N", sort="-x", title=None),
    x=alt.X("Lift vs avg:Q", title="ER difference vs account average (pp)"),
    color=alt.condition("datum['Lift vs avg'] >= 0", alt.value(T.ACCENT), alt.value(T.NEG)),
    tooltip=["Hashtag", alt.Tooltip("ER %:Q", format=".3f"), alt.Tooltip("Lift vs avg:Q", format="+.3f")])
c2.altair_chart(lift.properties(height=300, width="container", title="Engagement-rate lift by hashtag"), theme=None)

er_bar = alt.Chart(h).mark_bar(size=26, color=T.ACCENT).encode(
    y=alt.Y("Hashtag:N", sort="-x", title=None), x=alt.X("ER %:Q", title="Weighted ER %"),
    tooltip=["Hashtag", alt.Tooltip("ER %:Q", format=".2f")])
er_txt = alt.Chart(h).mark_text(align="left", dx=5, color=T.INK).encode(
    y=alt.Y("Hashtag:N", sort="-x"), x="ER %:Q", text=alt.Text("ER %:Q", format=".2f"))
reach_bar = alt.Chart(h).mark_bar(size=26, color="#9085e9").encode(
    y=alt.Y("Hashtag:N", sort="-x", title=None), x=alt.X("AvgReach:Q", title="Avg reach per post"),
    tooltip=["Hashtag", alt.Tooltip("AvgReach:Q", format=",.0f")])
c3, c4 = st.columns(2)
c3.altair_chart((er_bar + er_txt).properties(height=260, width="container", title="Engagement rate by hashtag"), theme=None)
c4.altair_chart(reach_bar.properties(height=260, width="container", title="Average reach by hashtag"), theme=None)

st.subheader("How many hashtags, and which combinations?")
n = (df.groupby("No. of Hashtags").agg(Posts=("Post No", "size"), E=("Engagements", "sum"), R=("Reach", "sum"))
     .reset_index())
n["ER %"] = n["E"] / n["R"] * 100
n["Tags"] = n["No. of Hashtags"].astype(str) + " tag(s)"
nbar = alt.Chart(n).mark_bar(size=50, color=T.ACCENT).encode(
    x=alt.X("Tags:N", title=None, axis=alt.Axis(labelAngle=0)), y=alt.Y("ER %:Q", title="Weighted ER %"),
    tooltip=["Tags", alt.Tooltip("ER %:Q", format=".3f"), alt.Tooltip("Posts:Q", format=",")])
ntxt = alt.Chart(n).mark_text(dy=-10, color=T.INK).encode(x="Tags:N", y="ER %:Q", text=alt.Text("ER %:Q", format=".2f"))

combo = df.assign(Combo=df["Tag List"].apply(" + ".join))
cb = (combo.groupby("Combo").agg(Posts=("Post No", "size"), E=("Engagements", "sum"), R=("Reach", "sum"))
      .reset_index())
cb["ER %"] = cb["E"] / cb["R"] * 100
cb = cb[cb["Posts"] >= 100]
c5, c6 = st.columns([1, 1.6])
c5.altair_chart((nbar + ntxt).properties(height=300, width="container", title="ER by number of hashtags"), theme=None)
with c6:
    st.markdown("**Best and worst hashtag combinations** (min 100 posts)")
    view = st.radio("Show", ["Best 8", "Worst 8"], horizontal=True, label_visibility="collapsed")
    table = cb.nlargest(8, "ER %") if view == "Best 8" else cb.nsmallest(8, "ER %")
    st.dataframe(table[["Combo", "Posts", "ER %"]], hide_index=True, column_config={
        "ER %": st.column_config.ProgressColumn(format="%.2f", min_value=float(cb["ER %"].min()) - 0.2,
                                                max_value=float(cb["ER %"].max()))})

best = h.loc[h["ER %"].idxmax()]
worst = h.loc[h["ER %"].idxmin()]
best_n = n.loc[n["ER %"].idxmax(), "Tags"]
T.takeaway(f"<b>{best['Hashtag']}</b> lifts ER the most ({best['Lift vs avg']:+.2f} pp) and <b>{worst['Hashtag']}</b> "
           f"the least ({worst['Lift vs avg']:+.2f} pp). Usage is evenly spread, so the brand is not leaning on its best tag. "
           f"Posts with <b>{best_n}</b> perform best — avoid single-hashtag posts.")
