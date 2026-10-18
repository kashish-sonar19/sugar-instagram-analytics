"""Task 1 (KPI overview) + Task 2 (monthly posting trend)."""

import altair as alt
import streamlit as st

from src import theme as T
from src.data import summarise, weighted_er
from src.state import filtered, filter_caption

T.header("KPIs & Posting Trend", "Task 1 · how is the account performing?  ·  Task 2 · how consistently does it post?")
df, _ = filtered()
filter_caption(df)
if df.empty:
    st.warning("No posts match the filters.")
    st.stop()

# ---------------- Task 1 ----------------
st.subheader("1 · KPI Overview")
T.kpi_cards([
    ("Total posts", f"{len(df):,}", f"{df['Post Date'].dt.date.nunique()} posting days"),
    ("Total likes", T.human(df["Likes"].sum(), 2), f"{df['Likes'].mean():,.0f} per post"),
    ("Total comments", T.human(df["Comments"].sum(), 2), f"{df['Comments'].mean():,.0f} per post"),
    ("Total reach", T.human(df["Reach"].sum(), 2), f"{df['Reach'].mean():,.0f} per post"),
    ("Engagement rate", f"{weighted_er(df):.2f}%", f"Σ engagements ÷ Σ reach · post mean {df['ER %'].mean():.2f}%"),
])
st.write("")
T.kpi_cards([
    ("Impressions", T.human(df["Impressions"].sum(), 2), f"reach = {df['Reach'].sum() / df['Impressions'].sum():.1%} of impressions"),
    ("Shares", T.human(df["Shares"].sum(), 2), f"share rate {df['Shares'].sum() / df['Reach'].sum():.2%}"),
    ("Saves", T.human(df["Saves"].sum(), 2), f"save rate {df['Saves'].sum() / df['Reach'].sum():.2%}"),
    ("Profile visits", T.human(df["Profile Visits"].sum(), 2), f"{df['Profile Visits'].sum() / df['Reach'].sum():.2%} of reach"),
    ("Follows", T.human(df["Follows"].sum(), 2), f"{df['Follows'].sum() / df['Profile Visits'].sum():.1%} of profile visits"),
])
st.write("")

mix = (df[["Likes", "Comments", "Shares", "Saves"]].sum().rename("Total").reset_index()
       .rename(columns={"index": "Action"}))
mix["Share"] = mix["Total"] / mix["Total"].sum() * 100
donut = alt.Chart(mix).mark_arc(innerRadius=62, outerRadius=110, stroke=T.SURFACE, strokeWidth=2).encode(
    theta="Total:Q",
    color=alt.Color("Action:N", scale=alt.Scale(domain=["Likes", "Comments", "Shares", "Saves"],
                                                range=["#199e70", "#c98500", "#9085e9", "#d55181"]),
                    legend=alt.Legend(orient="right")),
    tooltip=["Action", alt.Tooltip("Total:Q", format=","), alt.Tooltip("Share:Q", format=".1f", title="% of engagement")],
).properties(height=280, title="Engagement mix")
mix["Label"] = mix["Share"].map(lambda v: f"{v:.1f}%")
labels = alt.Chart(mix).mark_text(radius=132, color=T.INK).encode(
    theta=alt.Theta("Total:Q", stack=True), text="Label:N")
c1, c2 = st.columns([1, 1.3])
c1.altair_chart((donut + labels).properties(width="container", height=300), theme=None)
with c2:
    st.markdown("#### Reading the KPIs")
    st.markdown(f"""
- The account averages **{df['Reach'].mean():,.0f} reach** and **{df['Likes'].mean():,.0f} likes** per post.
- **{mix.loc[0, 'Share']:.0f}%** of all engagement is likes — saves ({mix.loc[3, 'Share']:.1f}%) and shares ({mix.loc[2, 'Share']:.1f}%) are small.
- Engagement rate is shown two ways: **weighted** ({weighted_er(df):.2f}%, total engagements ÷ total reach — the account-level rate)
  and **post mean** ({df['ER %'].mean():.2f}%). They are almost identical, so the KPI is robust.
""")

# ---------------- Task 2 ----------------
st.subheader("2 · Monthly Posting Trend")
m = summarise(df, ["Month", "Month Name"]).sort_values("Month")
m["MoM %"] = m["Posts"].pct_change() * 100

line = alt.Chart(m).mark_area(
    line={"color": T.ACCENT}, color=alt.Gradient(gradient="linear", stops=[
        alt.GradientStop(color=T.SURFACE, offset=0), alt.GradientStop(color="#146b4f", offset=1)],
        x1=1, x2=1, y1=1, y2=0),
    point={"color": T.ACCENT, "size": 60},
).encode(
    x=alt.X("Month Name:N", sort=m["Month Name"].tolist(), title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y("Posts:Q", title="Posts published"),
    tooltip=["Month Name", alt.Tooltip("Posts:Q", format=","), alt.Tooltip("ER %:Q", format=".2f")],
).properties(height=300, width="container", title="Posts per month")
st.altair_chart(line, theme=None)

chg = m.dropna(subset=["MoM %"])
bars = alt.Chart(chg).mark_bar().encode(
    x=alt.X("Month Name:N", sort=m["Month Name"].tolist(), title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y("MoM %:Q", title="% change in posts"),
    color=alt.condition("datum['MoM %'] >= 0", alt.value(T.ACCENT), alt.value(T.NEG)),
    tooltip=["Month Name", alt.Tooltip("MoM %:Q", format="+.1f")],
).properties(height=220, width="container", title="Month-over-month change in posting volume")
st.altair_chart(bars, theme=None)

full = m.iloc[1:-1] if len(m) > 2 else m
daily = df.groupby(df["Post Date"].dt.date).size()
T.takeaway(f"Output is very consistent — about <b>{full['Posts'].mean():,.0f} posts per full month</b> and "
           f"{daily.mean():.0f} per day (day-to-day variation only {daily.std() / daily.mean():.0%}). "
           f"The big swings are only in the first and last months, which are partial. "
           f"Monthly ER stays between {m['ER %'].min():.2f}% and {m['ER %'].max():.2f}%.")
with st.expander("Monthly table"):
    st.dataframe(m[["Month Name", "Posts", "Reach", "Engagements", "ER %", "Save Rate %", "Follows"]].round(2),
                 hide_index=True)
