"""Task 5 – Post format performance comparison."""

import altair as alt
import streamlit as st

from src import theme as T
from src.data import summarise
from src.state import filtered, filter_caption

T.header("Post Formats", "Task 5 · Image vs Reel vs Story vs Video")
df, _ = filtered()
filter_caption(df)
if df.empty:
    st.stop()

per_post = (df.groupby("Post Type").agg(Posts=("Post No", "size"), Likes=("Likes", "mean"),
                                         Comments=("Comments", "mean"), Saves=("Saves", "mean"),
                                         Shares=("Shares", "mean"), Reach=("Reach", "mean"))
            .reset_index())

st.subheader("Average likes, comments and saves per post")
metric = st.radio("Metric", ["Likes", "Comments", "Saves", "Shares"], horizontal=True, label_visibility="collapsed")
bar = alt.Chart(per_post).mark_bar(size=48).encode(
    x=alt.X("Post Type:N", title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y(f"{metric}:Q", title=f"Avg {metric.lower()} per post"),
    color=alt.Color("Post Type:N", scale=T.FORMAT_SCALE, legend=None),
    tooltip=["Post Type", alt.Tooltip(f"{metric}:Q", format=",.1f"), alt.Tooltip("Posts:Q", format=",")])
lbl = alt.Chart(per_post).mark_text(dy=-10, color=T.INK).encode(
    x="Post Type:N", y=f"{metric}:Q", text=alt.Text(f"{metric}:Q", format=",.0f"))
st.altair_chart((bar + lbl).properties(height=300, width="container", title=f"Avg {metric} by format"), theme=None)

# grouped bars on a common scale: performance index (100 = account average)
st.subheader("Performance index by format (100 = account average)")
idx = per_post.copy()
for c in ["Likes", "Comments", "Saves", "Shares"]:
    idx[c] = idx[c] / df[c].mean() * 100
long = idx.melt(id_vars="Post Type", value_vars=["Likes", "Comments", "Saves", "Shares"],
                var_name="Metric", value_name="Index")
grouped = alt.Chart(long).mark_bar().encode(
    x=alt.X("Metric:N", title=None, axis=alt.Axis(labelAngle=0)),
    xOffset="Post Type:N",
    y=alt.Y("Index:Q", title="Index", scale=alt.Scale(domain=[min(95, long["Index"].min() - 1),
                                                           max(105, long["Index"].max() + 1)], clamp=True)),
    color=alt.Color("Post Type:N", scale=T.FORMAT_SCALE, title="Format"),
    tooltip=["Post Type", "Metric", alt.Tooltip("Index:Q", format=".1f")])
rule = alt.Chart().mark_rule(color=T.INK_2, strokeDash=[4, 4]).encode(y=alt.datum(100))
st.altair_chart(alt.layer(grouped, rule, data=long).properties(height=320, width="container",
                title="Grouped bars: each metric indexed to the account average (axis zoomed to 95–105)"),
                theme=None)
st.caption("Indexing puts likes (~2,950) and saves (~177) on one comparable scale. The axis is zoomed — "
           "differences are a few percent at most.")

st.subheader("Rates by format (weighted)")
s = summarise(df, "Post Type")
st.dataframe(s[["Post Type", "Posts", "ER %", "ER Index", "Save Rate %", "Share Rate %", "Follow Rate %"]].round(3),
             hide_index=True)

best = s.loc[s["ER %"].idxmax()]
worst = s.loc[s["ER %"].idxmin()]
best_save = s.loc[s["Save Rate %"].idxmax(), "Post Type"]
best_share = s.loc[s["Share Rate %"].idxmax(), "Post Type"]
T.takeaway(f"<b>{best['Post Type']}</b> has the best weighted ER ({best['ER %']:.2f}%, index {best['ER Index']:.1f}); "
           f"<b>{worst['Post Type']}</b> is lowest ({worst['ER %']:.2f}%). {best_save} earns the most saves per reach and "
           f"{best_share} the most shares. All formats sit within ±1% of the average, so format is a fine-tuning lever, "
           "not a growth lever.")
