"""Task 6 – Day-of-week analysis."""

import altair as alt
import streamlit as st

from src import theme as T
from src.data import DAY_ORDER, summarise
from src.state import filtered, filter_caption

T.header("Best Days to Post", "Task 6 · average engagement by weekday")
df, _ = filtered()
filter_caption(df)
if df.empty:
    st.stop()

d = summarise(df, "Day")
d["Day"] = d["Day"].astype(str)
best_day = d.loc[d["ER %"].idxmax(), "Day"]

bars = alt.Chart(d).mark_bar(size=46).encode(
    x=alt.X("Day:N", sort=DAY_ORDER, title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y("ER %:Q", title="Engagement rate %"),
    color=alt.condition(f"datum.Day == '{best_day}'", alt.value(T.ACCENT_HI), alt.value(T.ACCENT)),
    tooltip=["Day", alt.Tooltip("ER %:Q", format=".3f"), alt.Tooltip("Posts:Q", format=",")])
txt = alt.Chart(d).mark_text(dy=-10, color=T.INK).encode(
    x=alt.X("Day:N", sort=DAY_ORDER), y="ER %:Q", text=alt.Text("ER %:Q", format=".2f"))
st.altair_chart((bars + txt).properties(height=320, width="container", title="Weighted engagement rate by weekday"),
                theme=None)

c1, c2 = st.columns(2)
dev = d.assign(Index=d["ER Index"] - 100)
dev_chart = alt.Chart(dev).mark_bar(size=34).encode(
    x=alt.X("Day:N", sort=DAY_ORDER, title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y("Index:Q", title="% above / below average"),
    color=alt.condition("datum.Index >= 0", alt.value(T.ACCENT), alt.value(T.NEG)),
    tooltip=["Day", alt.Tooltip("Index:Q", format="+.2f")])
c1.altair_chart(dev_chart.properties(height=280, width="container", title="ER vs account average (%)"), theme=None)

vol = alt.Chart(d).mark_bar(size=34, color="#9085e9").encode(
    x=alt.X("Day:N", sort=DAY_ORDER, title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y("Posts:Q", title="Posts"), tooltip=["Day", alt.Tooltip("Posts:Q", format=",")])
c2.altair_chart(vol.properties(height=280, width="container", title="Posting volume by weekday"), theme=None)

st.subheader("Best format for each day")
grid = summarise(df, ["Day", "Post Type"])
grid["Day"] = grid["Day"].astype(str)
heat = alt.Chart(grid).mark_rect(stroke=T.SURFACE, strokeWidth=2).encode(
    x=alt.X("Day:N", sort=DAY_ORDER, title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y("Post Type:N", title=None),
    color=alt.Color("ER %:Q", scale=alt.Scale(range=T.SEQ), title="ER %"),
    tooltip=["Day", "Post Type", alt.Tooltip("ER %:Q", format=".2f"), alt.Tooltip("Posts:Q", format=",")])
mid = (grid["ER %"].min() + grid["ER %"].max()) / 2
htxt = alt.Chart(grid).mark_text(fontSize=12).encode(
    x=alt.X("Day:N", sort=DAY_ORDER), y="Post Type:N", text=alt.Text("ER %:Q", format=".2f"),
    color=alt.condition(f"datum['ER %'] > {mid}", alt.value("#0b0b0b"), alt.value(T.INK)))
st.altair_chart((heat + htxt).properties(height=230, width="container", title="Weighted ER: day × format"),
                theme=None)

top_slots = grid.nlargest(3, "ER %")
wk = df.groupby("Is Weekend")[["Engagements", "Reach"]].sum()
wk_er = wk["Engagements"] / wk["Reach"] * 100
worst = d.loc[d["ER %"].idxmin()]
T.takeaway(f"<b>{best_day}</b> is the strongest day ({d['ER %'].max():.2f}%) and <b>{worst['Day']}</b> the weakest "
           f"({worst['ER %']:.2f}%). Weekend vs weekday: {wk_er.get(True, float('nan')):.2f}% vs "
           f"{wk_er.get(False, float('nan')):.2f}%. Best slots: "
           + ", ".join(f"{r['Post Type']} on {r['Day']} ({r['ER %']:.2f}%)" for _, r in top_slots.iterrows())
           + ". The spread is small, so timing should support — not replace — good content.")
